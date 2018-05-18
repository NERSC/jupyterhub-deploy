#!/opt/anaconda3/bin/python

import socket
sock = socket.socket()
sock.bind(('', 0))
print(sock.getsockname()[1])
sock.close()
