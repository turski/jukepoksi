from glob import glob
from audiofile import audiofile, is_supported
import mutagen, pymongo, os

class Collection(object):
    def __init__(self, librarypath, dbname='jukepoksi'):
        self.db = pymongo.Connection()[dbname]
        self.ids = []
        for t in self.db.tracks.find():
            self.ids.append(t['_id'])
        self.librarypath = librarypath

    def add_path(self, path):
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.exists(path):
            if os.path.isdir(path):
                self.add_dir(path)
            elif os.path.isfile(path):
                try:
                    self.add_file(path)
                except ValueError:
                    pass

    def add_dir(self, path):
        l = glob(path + '/*')
        l.sort()
        for f in l:
            self.add_path(f)

    def add_file(self, path):
        filename = os.path.basename(path)
        filetype = filename.rsplit('.', 1)[1]
        if not is_supported(filetype):
            raise ValueError, 'Unsupported filetype: %s' % (filetype)
        entry = dict( filepath = path,
                      filename = filename,
                      filetype = filetype)
        try:
            f = mutagen.File(path, easy=True)
        except:
            f = None
        if f:
            fileinfo = dict( album = f.tags.get('album'),
                            artist = f.tags.get('artist'),
                           bitrate = getattr(f.info, 'bitrate', 0),
                       description = f.tags.get('description'),
                             genre = f.tags.get('genre'),
                            length = getattr(f.info, 'length', 0.0),
                             title = f.tags.get('title'),
                       tracknumber = f.tags.get('tracknumber') )
            entry.update(fileinfo)
        self.insert('tracks', entry)

    def insert(self, collection, entry):
        entry.update(entry_id = len(self.ids))
        try:
            oid = self.db[collection].insert(entry)
        except pymongo.errors.InvalidStringData:
            return
        print "Indexed %s" % (entry['filepath'])
        self.ids.append(oid)

    def open(self, id):
        oid = self.ids[id]
        track = self.db.tracks.find_one(oid)
        print 'DEBUG: Opening file: %s' % (track['filepath'])
        return audiofile(track['filepath'].encode('utf-8'))

    def update(self):
        self.db.drop_collection('tracks')
        self.add_path(self.librarypath)

