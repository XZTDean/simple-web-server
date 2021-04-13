from socket import *
import struct
import time
import os


class BadRequest(Exception):
    pass


def wrong_request_method(method: str) -> bool:
    method_list = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE']
    return method not in method_list


def response_header_200(length, modify_time):
    return b'HTTP/1.1 200 OK\r\nDate: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()).encode()\
             + b'\r\nContent-Length: ' + str(length).encode() + b'\r\nCache-Control: no-cache\r\nLast-Modified: '\
             + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(modify_time)).encode() + b'\r\n\r\n'


def response_header_304():
    pass


def response_header_400():
    pass


def response_header_404():
    pass


def response_header_408():
    pass


def process_request(data):
    request = data.decode()
    header_end = request.find('\r\n\r\n')
    if header_end <= 0:
        raise BadRequest
    header = request[:header_end].split('\r\n')
    req_info = header[0].split(' ')
    if 'HTTP' not in req_info[2] or wrong_request_method(req_info[0]):
        raise BadRequest
    content, modify_time = file_handle(req_info[1])
    response_header = response_header_200(len(content), modify_time)
    return response_header + content


def file_handle(path):
    file_dir = path[1:]
    file_stats = os.stat(file_dir)
    modify_time = file_stats.st_mtime
    file = open(file_dir, "rb")
    content = file.read()
    file.close()
    return content, modify_time


def handle_conn(conn):
    conn.settimeout(30)
    while True:
        try:
            print("enter recv part")
            data = conn.recv(1024)
            print(data)
            response = process_request(data)
            conn.sendall(response)
            print("sent")
        except:
            break
    conn.close()
#b'HTTP/1.1 200 OK\r\ncache-control: public, max-age=7200\r\nContent-Length: 12\r\nConnection: Keep-Alive\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\nHello World!\r\n'

def start():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    (connection, address) = s.accept()
    handle_conn(connection)


start()