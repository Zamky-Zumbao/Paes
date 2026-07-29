import sys 
import os 
from http.server import HTTPServer, BaseHTTPRequestHandler 
import json 
 
class handler(BaseHTTPRequestHandler): 
    def do_GET(self): 
        self.send_response(200) 
        self.send_header('Content-type', 'text/html') 
        self.end_headers() 
        self.wfile.write(html.encode()) 
