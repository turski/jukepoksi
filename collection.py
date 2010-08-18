from glob import glob, iglob
from audiofile import audiofile
from tools import mtime, is_supported, Logger
from pymongo.errors import InvalidStringData
import mutagen, pymongo, os

class Collection(object):
    def __init__(self, rootdir, dbname='jukepoksi'):
        self.rootdir = os.path.abspath(os.path.expandvars(os.path.expanduser(rootdir)))
        self.db = pymongo.Connection()[dbname]
        self.f_id = []
        self.d_id = []
        self.logger = Logger()
        #for t in self.db.tracks.find():
            #self.ids.append(t['_id'])

    def _insert(self, collection, entry):
        entry.update(entry_id = len(self.ids))
        try:
            oid = self.db[collection].insert(entry)
            print 'DEBUG: Inserted entry %s into collection %s' % (entry, collection)
            self.ids.append(oid)
        except pymongo.errors.InvalidStringData:
            pass

    def _file_entry(self, path):
        assert os.path.isfile(path)
        filedir = os.path.dirname(path)
        filename = os.path.basename(path)
        filetype = os.path.splitext(filename)[1]
        entry = { 'f_id' : len(self.f_id),
                 'fpath' : path,
                 'fname' : filename,
                 'ftype' : filetype }
        try:
            f = mutagen.File(path, easy=True)
        except:
            f = None
        if f:
            fileinfo = { 'album' : f.tags.get('album'),
                        'artist' : f.tags.get('artist'),
                       'bitrate' : getattr(f.info, 'bitrate', 0),
                   'description' : f.tags.get('description'),
                         'genre' : f.tags.get('genre'),
                        'length' : getattr(f.info, 'length', 0.0),
                         'mtime' : mtime(path),
                         'title' : f.tags.get('title'),
                   'tracknumber' : f.tags.get('tracknumber') }
            entry.update(fileinfo)
        return entry

    def _dir_entry(self, path, dirs, files):
        assert os.path.isdir(path)
        entry = { 'd_id' : len(self.d_id),
                 'dname' : path,
                  'dirs' : dirs,
                 'files' : files,
                 'mtime' : mtime(path) }
        return entry

    def _insert_file(self, path):
        assert os.path.isfile(path)
        self.logger.inc()
        self.logger.log('Adding file: %s ... ' % (path), newline=False)
        f_entry = self._file_entry(path)
        try:
            f_oid = self.db.files.insert(f_entry)
            self.f_id.append(f_oid)
            self.logger.log('Done')
        except InvalidStringData:
            self.logger.log('ERROR, paskaa')
            f_oid = None
        finally:
            self.logger.dec()
            return f_oid

    def _insert_dir(self, dirname):
        assert os.path.isdir(dirname)
        self.logger.inc()
        self.logger.log('Entering dir: %s' % (dirname))
        files = []
        dirs = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isfile(path):
                if is_supported(path):
                    f_oid = self._insert_file(path)
                    if f_oid:
                        files.append(f_oid)
            elif os.path.isdir(path):
                d_oid = self._insert_dir(path)
                if d_oid:
                    self.d_id.append(d_oid)
                    dirs.append(d_oid)
        d_entry = self._dir_entry(dirname, dirs, files)
        d_oid = self.db.dirs.insert(d_entry)
        self.logger.log('Leaving dir: %s' % (dirname))
        self.logger.dec()
        return d_oid

    def update(self):
        self.logger.inc()
        self.logger.log('Starting database update')
        self.db.files.drop()
        self.db.dirs.drop()
        self._insert_dir(self.rootdir)
        self.logger.log('Database update done')
        self.logger.dec()

    def open(self, f_id):
        f_oid = self.f_id[f_id]
        ffile = self.db.files.find_one(f_oid)
        print 'DEBUG: Opening file: %s' % (ffile['fpath'])
        return audiofile(ffile['fpath'].encode('utf-8'))


