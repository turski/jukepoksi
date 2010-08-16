#!/usr/bin/env python

import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 50666))
s.send(sys.argv[1])
print s.recv(4096)
s.close()