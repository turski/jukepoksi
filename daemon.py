#!/usr/bin/env python
import sys
from audiofile import audiofile
from output import AlsaOutput
from collection import Collection
from threading import Thread, Lock
import os
import time

import socket

class Daemon(object):
    def __init__(self, conf):
        self.conf = conf
        self.collection = Collection(conf['librarypath'])
        self.output = AlsaOutput()
        self.player = Player(self.output)
        self.play_thread = None
        self.host = conf['host']
        self.port = conf['port']
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commands = dict( GC = self.get_collection,
                               P = self.play,
                               Q = self.queue,
                               S = self.stop,
                               U = self.update )

    def run(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print "Listening on port %i" % (self.port)
        while True:
            conn, addr = self.socket.accept()
            print "connected"
            try:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    else:
                        reply = self.parse(data)
                        if not reply:
                            reply = ['FAIL']
                        for line in reply:
                            conn.send(str(line))
            except:
                conn.close()
                self.socket.close()
                raise
            conn.close()

    def parse(self, data):
        datalist = data.split('|')
        cmd = datalist[0]
        args = datalist[1:]
        if cmd in self.commands:
            print 'DEBUG: Command %s with args: %s' % (cmd, args)
            reply = self.commands[cmd](*args)
        else:
            print 'DEBUG: Invalid command'
            reply = ['FAIL']
        return reply

    def get_collection(self, *args):
        for entry in self.collection.db.tracks.find():
            yield entry

    def play(self, id, *args):
        afile = self.collection.open(int(id))
        self.player.load(afile)
        self.play_thread = Thread(target=self.player._play)
        self.player.status = 'play'
        self.play_thread.start()
        return ['OK']

    def queue(self, id, *args):
        return ['OK']

    def stop(self, *args):
        self.player.afile = None
        return ['OK']

    def update(self, *args):
        self.collection.update()
        return ['OK']


class Player(object):
    blocksize = 16

    def __init__(self, output):
        self.lock = Lock()
        self.afile = None
        self.status = 'stop'
        self.output = output

    def np(self):
        return "np: %s" % ('foo')

    def load(self, afile):
        self.afile = afile

    def _play(self):
        with self.lock:
            while self.status != 'stop':
                while self.status == 'pause':
                            time.sleep(0.1)
                if self.afile:
                    data = self.afile.read(self.blocksize)
                else:
                    break
                if data:
                    self.output.write(data)
                else:
                    self.afile = None
                    break


if __name__ == '__main__':
    conf = dict( librarypath = '~/musiikki',
                        host = 'localhost',
                        port = 50666 )
    d = Daemon(conf)
    d.run()