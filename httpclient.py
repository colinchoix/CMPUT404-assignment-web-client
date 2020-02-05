#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Colin Choi, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL] [BODY]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Try to parse response code from HTTP header. Return 500 if unable to parse
        try:
            code = data.split("\r\n\r\n")[0].split()[1]
            return int(code)
        except:
            return 500

    def get_headers(self,data):
        # Return empty string if response is improperly formatted
        try:
            headers = data.split("\r\n\r\n")[0]
            return headers
        except:
            return ""

    def get_body(self, data):
        # Return empty string if there isn't a body
        try:
            body = data.split("\r\n\r\n")[1]
            return body
        except:
            return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url = urlparse(url)
        # Use / for path if not specified in the url
        host, netlocation, port, path = url.hostname, url.netloc, url.port, "/" if url.path == "" else url.path

        if port == None: # Use defaults for http and https if port not specified
            port = 443 if url.scheme == "https" else 80
        
        self.connect(socket.gethostbyname( host ), port)

        # Build the HTTP GET request
        request = "GET "+path+" HTTP/1.1\r\nHost: "+netlocation+"\r\nConnection: keep-alive\r\nAccept-Charset: utf-8\r\nUser-Agent: python-httpclient\r\nAccept: */*\r\nAccept-Encoding: deflate\r\n\r\n"

        # Send the request and read the response
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # Parse out the Code and Body from the response
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = urlparse(url)
        # Use / for path if not specified in the url
        host, netlocation, port, path = url.hostname, url.netloc, url.port, "/" if url.path == "" else url.path

        if port == None: # Use defaults for http and https if port not specified
            port = 443 if url.scheme == "https" else 80
        
        self.connect(socket.gethostbyname( host ), port)

        # Check for and POST arguments and build the HTTP POST request
        if args == None:
            length = 0
            request = "POST "+path+" HTTP/1.1\r\nHost: "+netlocation+"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(length)+"\r\nConnection: keep-alive\r\nAccept-Charset: utf-8\r\nUser-Agent: python-httpclient\r\nAccept: */*\r\nAccept-Encoding: deflate\r\n\r\n"
        else:
            # Build body of POST request
            body = ""
            for x in args:
                body += x + "=" + args[x] + "&"
            # Remove the trailing ampersand
            body = body[:-1]

            length = len(body)
            request = "POST "+path+" HTTP/1.1\r\nHost: "+netlocation+"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(length)+"\r\nConnection: keep-alive\r\nAccept-Charset: utf-8\r\nUser-Agent: python-httpclient\r\nAccept: */*\r\nAccept-Encoding: deflate\r\n\r\n"
            request += body
        
        # Send the request and read the response
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # Parse out the Code and Body from the response
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ).body)
    elif (len(sys.argv) == 4):
        print(client.command( sys.argv[2], sys.argv[1], sys.argv[3]).body)
    else:
        print(client.command( sys.argv[1] ))
