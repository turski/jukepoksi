from decoder import MadDecoder, FlacDecoder, FaadDecoder, VorbisDecoder


class AudioFile(object):
    filetype = None
    _decoder = None

    def __init__(self, path):
        self.path = path
        self.decoder = self._decoder(path)

    def read(self, l):
        data = self.decoder.read(l)
        return data

    def close(self):
        self.decoder = None


class AacFile(AudioFile):
    filetype = 'aac'
    _decoder = FaadDecoder


class FlacFile(AudioFile):
    filetype = 'flac'
    _decoder = FlacDecoder


class Mp3File(AudioFile):
    filetype = 'mp3'
    _decoder = MadDecoder


class OggFile(AudioFile):
    filetype = 'ogg'
    _decoder = VorbisDecoder


def audiofile(afile_path):
    filetype = afile_path.rsplit('.', 1)[1].lower()
    filecls = filetypes.get(filetype)
    return filecls(afile_path)


filetypes = {'aac': AacFile,
            'flac': FlacFile,
             'mp3': Mp3File,
             'ogg': OggFile}