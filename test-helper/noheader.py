import socket

HOST = 'localhost'
PORT = 80

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello World!')
    data = s.recv(1024)
    s.close()
    print(data.decode())
