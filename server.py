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
        print ("Got a request of: %s\n" % self.data)

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
        request_method, request_path, protocol_version = fields[0].decode("ASCII").split(" ")
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

        # Check if the request method can be processed
        if not self.is_method_processed(request_method):
            status_code = "405 Method Not Allowed"
            server_response = protocol_version + " " + status_code
            self.request.sendall(bytearray(server_response, "utf-8"))

        # Check if the requested file and the local path to the requested file actually exists 
        if not self.file_or_directory_exists(request_path) or self.is_invalid_directory(request_path):
            status_code = "404 Not Found\r\n"
            server_response = protocol_version + " " + status_code
            self.request.sendall(bytearray(server_response, "utf-8"))

        # Find the local path to the file
        file_local_path = self.file_local_path_finder(request_path)
        file_content_type = self.file_content_type_identifier(file_local_path)
        try:
            file_content = self.file_content_reader(file_local_path)
        except IsADirectoryError:
            status_code = "301 Moved Permanently"
            server_response = protocol_version + " " + status_code + "Location: " + file_local_path + "/"
            self.request.sendall(bytearray(server_response, "utf-8"))

        # When the local path and requested file are valid
        status_code = "200 OK \r\n"
        server_response = protocol_version + " " + status_code + file_content_type + file_content
        self.request.sendall(bytearray(server_response, "utf-8"))
        # self.request.sendall(bytearray("OK",'utf-8'))
        # return

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

    def file_or_directory_exists(self, requestedFilePath):
        """
        Helper function for the webserver to check validness of the requested file or local path to the requested file 
        """
        file_local_path = "./www" + requestedFilePath
        if os.path.isdir(file_local_path) or os.path.isfile(file_local_path):
            return True
        else:
            return False

    def is_invalid_directory(self, requestedFilePath):
        """
        Helper function for the webserver to check validness of backward access to the requested file's directory (local path)
        """
        sub_directories = requestedFilePath.split("/")  
        if ".." in sub_directories:
            return True
        else:
            return False

    def file_local_path_finder(self, requestedFilePath):
        """
        Helper function for locating the requested file's path locally
        """
        file_local_path = "./www" + requestedFilePath
        if os.path.isfile(file_local_path):
            return file_local_path
        elif "index.html" in requestedFilePath:
            assert(os.path.isdir(file_local_path))
            return file_local_path + "index.html"
        elif "base.css" in requestedFilePath:
            assert(os.path.isdir(file_local_path))
            return file_local_path + "base.css"
        elif "deep.css" in requestedFilePath:
            return file_local_path + "deep.css"
            
    def file_type_identifier(self, fileLocalPath):
        # The file actually has a specific type
        if len(fileLocalPath.strip(".").split(".")) > 1:
            return fileLocalPath.strip(".").split(".")[1]
        else:
            return None

    def file_content_type_identifier(self, fileLocalPath):
        file_content_type = "Content-Type: "
        file_type = self.file_type_identifier(fileLocalPath)
        if file_type != None:
            if file_type == "html":
                file_content_type += "text/html; charset=utf-8"
            elif file_content_type == "css":
                file_content_type += "text/css; charset=utf-8"
        else: 
            file_content_type += "text/plain; charset=utf-8"
        return file_content_type + "\r\n"
        
    def file_content_reader(self, fileLocalPath):
        return "\r\n" + open(fileLocalPath, "r").read()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

