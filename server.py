#  coding: utf-8 
import socketserver
import os 
# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Shihao Liu
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
    
    def file_existence_checker(self, requested_file_path):
        """
        Helper function to check requested file existence
        """
        target_file_path = "./www" + requested_file_path
        return (os.path.exists(target_file_path))

    def backward_dir_access_checker(self, requested_file_path):
        """
        Check for backward directory access, ie /../../.. etc
        """
        dirs = requested_file_path.split("/")
        return (".." in dirs)

    def file_type_getter(self, requested_file_path):
        try:
            requested_file_type = requested_file_path.split(".")[1]
        except:
            return None
        # Here we only consider html and css file types
        if requested_file_type == "html":
            return "text/css; charset=utf-8\r\n"
        elif requested_file_type == "css":
            return "text/html; charset=utf-8\r\n"
        else:
            return "text/plain; charset=utf-8\r\n"

    def file_content_reader(self, requested_file_path):
        return open( "./www" + requested_file_path, "r").read()

    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)  
        # self.request.sendall(bytearray("OK",'utf-8'))
        # Parse the raw request 
        # to get request method, requested file path, protocol version 
        request_method, requested_file_path, protocol_version = self.data.decode("utf-8").split("\r\n")[0].split(" ")

        # Determine if request method is valid
        # Here only GET request method is acceptable
        if request_method == "GET":
            # if requested file exists and cannot be accessible backwards thru directories
            if self.file_existence_checker(requested_file_path) and (not self.backward_dir_access_checker(requested_file_path)):
                # Attempt to get requested file type and content
                server_response = protocol_version + " 200 OK\r\n"
                requested_file_type = self.file_type_getter(requested_file_path)
                if requested_file_type != None: # requested file type is either html or css
                                                # requested file path targets a file 
                    requested_file_content = self.file_content_reader(requested_file_path)
                else: # requested file path targets a file targets a directory
                    # If requested file path doesn't end with a "/"
                    if not requested_file_path.endswith("/"):
                    # if requested_file_path[-1] != "/":
                        # lead to a actual file path after adding a "/" at the end of requested file path string
                        # -> 301
                        server_response = protocol_version + " 301 Moved Permanently\r\n" + "Location: " + requested_file_path + "/\r\n"

                    # If requested file path string ends with "/"
                    # auto-provide index.html of target directory
                    requested_file_type = "text/html; charset=utf-8\r\n"
                    requested_file_content = self.file_content_reader(requested_file_path + "/index.html")

                # generate the rest of headers after webserver response 
                server_response += "Connection: Close\r\n"
                server_response += "Content-Length: " + str(len(requested_file_content)) + "\r\n"
                server_response += "Content-Type: " + requested_file_type + "\r\n"
                server_response += "\r\n\n" + requested_file_content
                self.request.sendall(bytearray(server_response,"utf-8"))
                # return 

            else: # Cannot locate the requested file -> 404 
                server_response = protocol_version + " 404 Not Found\r\n"
                self.request.sendall(bytearray(server_response,"utf-8"))
                return

        else: # When request method is invalid -> 405 
            server_response = protocol_version + " 405 Method Not Allowed\r\n"
            self.request.sendall(bytearray(server_response,"utf-8"))
            return
    

    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()