#!/usr/bin/env python
import mad, alsaaudio, sys, tagpy

audiofile = sys.argv[1]
filetype = audiofile.rsplit('.', 1)[1]

alsadev = alsaaudio.PCM()

try:
    tag = tagpy.FileRef(audiofile).tag()
    print "np: %s - %s" % (tag.artist, tag.title)
except ValueError:
    pass

decoder = None

if filetype == 'mp3':
    decoder = mad.MadFile(audiofile)

if decoder:
    while 1:
        buf = decoder.read(128)
        if buf == None:
            break
        alsadev.write(buf)
