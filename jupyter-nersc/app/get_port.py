#!/usr/bin/env python

import socket

sock = socket.socket()
sock.bind(('', 0))
print(sock.getsockname()[1])
sock.close()
