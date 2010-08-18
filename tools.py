from audiofile import filetypes
import os, sys

class Logger(object):
    def __init__(self, output=sys.stdout, ident='  '):
        self.ident = ident
        self.output = output
        self.level = 0
        self.emptyline = True

    def log(self, msg, newline=True, flush=True):
        if self.emptyline:
            ident = self.level * self.ident
        else:
            ident = ''
        if newline:
            self.emptyline = True
            nline = '\n'
        else:
            self.emptyline = False
            nline = ''
        self.output.write( ident + msg + nline )
        if flush:
            self.output.flush()

    def inc(self):
        self.level += 1

    def dec(self):
        self.level -= 1

def rlist_supported(path):
    files = []
    plist = os.listdir(path)
    plist.sort()
    for _p in plist:
        p = os.path.join(path, _p)
        if os.path.isdir(p):
            files += rlist(p)
        elif os.path.isfile(p):
            if is_supported(p):
                files.append(p)
    return files

def timer(cmd, times, *args):
    t1 = time.time()
    for i in range(times):
        cmd(*args)
    t2 = time.time()
    t = t2 - t1
    print "%i loops of %s took %f seconds" % (times, cmd, t)

def mtime(path):
    return os.stat(path).st_mtime

def is_supported(path):
    return os.path.splitext(path)[1].strip('.') in filetypes