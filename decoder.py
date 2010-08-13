import mad
from subprocess import Popen, PIPE


class Decoder(object):
    def read(self, blocksize):
        data = self.decoder.read(blocksize)
        return data


class MadDecoder(Decoder):
    def __init__(self, afile_path):
        self.decoder = mad.MadFile(afile_path)


class FlacDecoder(Decoder):
    def __init__(self, afile_path):
        self.decoder = Popen( ['flac', '-d', '-c', '--totally-silent',
                               afile_path], stdout=PIPE).stdout

class FaadDecoder(Decoder):
    def __init__(self, afile_path):
        self.decoder = Popen( ['faad', '-b1', '-f2', '-q', '-w',
                               afile_path], stdout=PIPE).stdout