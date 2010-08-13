#!/usr/bin/env python
import sys
from audiofile import audiofile
from output import AlsaOutput


class Player(object):
    blocksize = 4

    def __init__(self, path, output):
        self.path = path
        self.afile = audiofile(path)
        self.output = output

    def np(self):
        if self.afile.tag:
            return "np: %s - %s" % (self.afile.tag.artist, self.afile.tag.title)

    def play(self):
        while True:
            data = self.afile.read_block(self.blocksize)
            self.output.write(data)

    def pause(self):
        pass

    def stop(self):
        pass

if __name__ == '__main__':
    afile_path = sys.argv[1]
    output = AlsaOutput()
    player = Player(afile_path, output)
    print player.np()
    player.play()