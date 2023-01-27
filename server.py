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
        # Determine the requested file type
        # Attempt to get the requested file locally by the requested file's local path
        # If the requested file local path is invalid
        if not self.is_file_type(request_file_path) or self.is_legal_directory(request_file_path):
            
            status = "404 Not Found\r\n"
            response =  protocol_version + " " + status
            self.request.sendall(bytearray(response, "utf-8"))
            return

        # If the requested file's local path is valid
        local_file_path = self.file_local_path_finder(request_file_path)
        local_file_type = self.file_content_type_getter(local_file_path)
        local_file_content = self.file_content_reader(local_file_path)

        # invalid local file type
        if local_file_type not in ['html', 'css']:
            if request_file_path.endswith("/"):
                request_file_path += "index.html"
            else: 
                request_file_path += "/"
                status_code = "301 Moved Permanently\r\n" + "Location: " + request_file_path
                server_response =  protocol_version + " " + status_code + local_file_type + local_file_content
                self.request.sendall(bytearray(response, "utf-8"))
                return
        # The request method and requested file are valid
        status_code = "200 OK\r\n"
        server_response =  protocol_version + " " + status_code + local_file_type + local_file_content
        self.request.sendall(bytearray(response, "utf-8"))
        return
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("HTTP/1.0 200 OK",'utf-8'))

    def file_local_path_finder(self, request_file_path):
        local_file_path = "./www" + request_file_path
        if os.path.isfile(local_file_path): 
            return local_file_path
        


    def is_method_processed(self, request_method):
        """
        Check if our server can handle this request method
        """
        # Here only GET request method is valid
        if request_method == "GET":
            return True
        elif request_method == "PUT":
            return False
        elif request_method == "POST":
            return False
        elif request_method == "DELETE":
            return False
        else:
            return False
    
    def is_file_type(self, request_file_path):
        """
        Helper function to identify the requested file type 
        """
        # "/foobar.html".split(".")  -> ['/foobar', 'html']
        request_file_path_components = request_file_path.split(".")
        if (len(request_file_path_components) > 1): # If the request file path contains a file type
            return True
        else: 
            return False
    
    def file_exists(self, request_file_path):
        local_file_path = "./www" + request_file_path
        if os.path.isdir(local_file_path) or os.path.isfile(local_file_path):
            return True
        else:
            return False

    def is_legal_directory(self, request_file_path):
        """
        Check for backward directory access, ie /../../.. etc
        """
        dirs = request_file_path.split("/")
        if ".." in dirs:
            return True
        else:
            return False

    def file_content_type_getter(self, local_file_path):
        file_content_type = "Content: "
        local_file_path_components = local_file_path.split(".")
        if len(local_file_path_components) > 1:
            local_file_content_type = local_file_path_components[1]
        else: 
            local_file_content_type = None
        if local_file_content_type != None:
            if local_file_content_type == "html":
                file_content_type += "text/html; charset=utf-8"
            elif local_file_content_type == "css":
                file_content_type += "text/css; charset=utf-8"
        else:
            local_file_content_type += "text/plain; charset=utf-8"
        return file_content_type + "\r\n"

    def file_content_reader(self, local_file_path):
        return"\r\n" + open(local_file_path, "r").read()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()