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
             + b'\r\nConnection: keep-alive\r\nContent-Length: ' + str(length).encode() + b'\r\nCache-Control: '\
             + b'no-cache\r\nLast-Modified: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                                              time.gmtime(modify_time)).encode() + b'\r\n\r\n'


def response_header_304():
    return b'HTTP/1.1 304 Not Modified\r\nDate: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()).encode()\
           + b'\r\nCache-Control: no-cache\r\nConnection: keep-alive\r\n\r\n'


def response_header_400():
    return b'HTTP/1.1 400 Bad Request\r\nDate: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()).encode() \
           + b'\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nContent-Length: 15\r\n' \
           + b'Content-Type: text/plain; charset=utf-8\r\n\r\n400 Bad Request'


def response_header_404():
    return b'HTTP/1.1 404 Not Found\r\nDate: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()).encode() \
           + b'\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nContent-Length: 13\r\n'\
           + b'Content-Type: text/plain; charset=utf-8\r\n\r\n404 Not Found'


def response_header_408():
    return b'HTTP/1.1 408 Request Timeout\r\nDate: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()).encode() \
           + b'\r\nConnection: close\r\nCache-Control: no-cache\r\n\r\n'


def not_modified_since(header, modify_time):
    for line in header:
        if 'If-Modified-Since:' in line:
            time_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(modify_time))
            if time_str in line:
                return True
            else:
                return False
    return False


def process_request(data):
    request = data.decode()
    header_end = request.find('\r\n\r\n')
    if header_end <= 0:
        print('EMPTY')
        raise BadRequest
    header = request[:header_end].split('\r\n')
    req_info = header[0].split(' ')
    if 'HTTP' not in req_info[2] or wrong_request_method(req_info[0]):
        raise BadRequest
    try:
        content, modify_time = file_handle(req_info[1])
    except FileNotFoundError:
        return response_header_404()
    if not_modified_since(header, modify_time):
        print("return 304")
        return response_header_304()
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
    conn.settimeout(30)  # TCP connection will timeout in 30 seconds
    while True:
        try:
            print("enter recv part")
            data = conn.recv(1024)
            print(data)
            # if len(data) > 0:
            response = process_request(data)
            conn.sendall(response)
            print("sent")
        except:
            break
    conn.close()


def start():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    while True:
        (connection, address) = s.accept()
        handle_conn(connection)


start()
