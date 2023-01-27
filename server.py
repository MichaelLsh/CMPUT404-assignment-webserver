#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        """
        Citation for the following code block
        Author: Liam Kelly https://stackoverflow.com/users/1987437/liam-kelly
        URL: https://stackoverflow.com/questions/39090366/how-to-parse-raw-http-request-in-python-3
        License: MIT License
        Data&Time: 25/1/2023 @ 5 pm
        """
        # ========================================================================================= #
        # Parse the raw request 
        fields = self.data.split(b"\r\n")
        request_method_type, request_file_path, protocol_version = fields[0].decode("ASCII").split(" ")
        
        headers = fields[1:] # Ignore the GET / HTTP/1.1
        output = {}

        # Split each line by http key-value pairs, decode from bytes to char
        for each_header in headers:
            items = each_header.split(b":")
            key = items[0].decode("ASCII")
            values = items[1:]
            for i in range(len(values)):
                values[i] = values[i].decode("ASCII")
            output[key] = values
        # ========================================================================================= #

        # Determine if request method type is valid 
        if not self.is_method_processed(request_method_type):
            status_code = "405 Method Not Allowed"
            server_response = protocol_version + " " + status_code
            self.request.sendall(bytearray(server_response, "utf-8"))

        # If the request method type is valid
        # 
        print(request_file_path)
        
        # print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))

    def is_method_processed(self, requestMethod):
        """
        Check if our server can handle this request method
        """
        if requestMethod == "GET":
            return True
        elif requestMethod == "PUT":
            return False
        elif requestMethod == "POST":
            return False
        elif requestMethod == "DELETE":
            return False
        else:
            return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()