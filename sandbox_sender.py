import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall('DISCOVER ME')
    data = s.recv(10240)
    print('Received', repr(data))

