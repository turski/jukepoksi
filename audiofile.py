from decoder import MadDecoder, FlacDecoder, FaadDecoder
import tagpy

def audiofile(afile_path):
    filetype = afile_path.rsplit('.', 1)[1].lower()
    filecls = filetypes.get(filetype)
    return filecls(afile_path)


class AudioFile(object):
    filetype = None

    def read_block(self, l):
        data = self.decoder.read(l)
        return data


class Mp3File(AudioFile):
    filetype = 'mp3'
    def __init__(self, path):
        self.path = path
        self.decoder = MadDecoder(path)
        self.tag = tagpy.FileRef(path).tag()


class FlacFile(AudioFile):
    filetype = 'flac'
    def __init__(self, path):
        self.path = path
        self.decoder = FlacDecoder(path)
        self.tag = tagpy.FileRef(path).tag()


class AacFile(AudioFile):
    filetype = 'aac'
    def __init__(self, path):
        self.path = path
        self.decoder = FaadDecoder(path)
        self.tag = None #tagpy.FileRef(path).tag()

filetypes = {'aac': AacFile,
            'flac': FlacFile,
             'mp3': Mp3File}