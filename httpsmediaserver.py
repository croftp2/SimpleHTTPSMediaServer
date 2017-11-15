#!/usr/bin/python

import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import os
import base64
from pprint import pformat, pprint
import ssl
import sys
import SocketServer
from urllib import unquote

key = ""
CERTFILE_PATH = ""

FILES = []
MEDIA_DIR = ""

COMMON_CSS=open("html_files/common_css.txt").read()

class AuthHandler(SimpleHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''
    def do_HEAD(self):
        print "send header"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        print "send header"
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Input username and password\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers.getheader('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
            return
#        elif self.headers.getheader('Authorization') == 'Basic '+key:
        elif self.headers.getheader('Authorization') in keys:
            print "Authed request for", self.path
            if self.path == "/":#Base dir
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                dirs = os.listdir(MEDIA_DIR)

                main_html = open("html_files/main.html").read()
                list_html = ""
                list_html += ''.join(sorted(["""
<div class="img_and_a">
  <a href="/title/{titlename}" class="link_img">
    <img src='/images/{titlename}/splash.jpg' class="img_fixed_size">
  </a>
  <br>
  <h3>{titlename}</h3>
</div>
""".format(titlename=i) for i in dirs]))
                list_html += ""
                self.wfile.write(main_html.format(list_html=list_html,common_css=COMMON_CSS))

            else:#not base
                fields = self.path.split('/', 2)
                print fields, MEDIA_DIR, MEDIA_DIR.strip('/')
                if fields[1] == "title":#video's html page
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    title_html = open("html_files/title.html")
                    name = unquote(fields[2])
                    print "Name", name
                    year = open(MEDIA_DIR + "/" + name + "/year.txt").read().strip()
                    body_html = "<center>{}</center>"
                    list_item = "<video controls><source src='/file/{dirname}/{filename}' type='video/mp4'></video>"
                    audio_item = "<audio controls><source src='/file/{dirname}/{filename}' type='audio/mpeg'></audio>"

                    dir_files = os.listdir(MEDIA_DIR + '/' + name)
                    audio_files = filter(lambda x:x[-4:] == '.mp3', dir_files)
                    dir_files = filter(lambda x:x[-4:] == '.mp4', dir_files)
                    dir_lines = '\n'.join(map(lambda x:list_item.format(filename=x,dirname=name), dir_files))
                    audio_lines = '\n'.join(map(lambda x:list_item.format(filename=x,dirname=name), audio_files))

#                    body_html = body_html.format(filename="/file/" + name + '/' + dir_files[0])
                    body_html = body_html.format(dir_lines + audio_lines)

                    self.wfile.write(title_html.read().format(name=name, year=year, body_html=body_html,common_css=COMMON_CSS))


                elif fields[1] == "file" and ".." not in fields[2]:#file
                    filename = MEDIA_DIR + unquote(fields[2])
                    filelen = os.stat(filename).st_size

                    byterange = self.headers.getheader("Range")
                    byterange = byterange.split("=")[1]
                    lowbyte, highbyte = byterange.split('-')
                    lowbyte = int(lowbyte)
                    highbyte = highbyte.strip()
                    if highbyte:
                        highbyte = int(highbyte)
                    else:
                        highbyte = filelen - 1


                    self.send_response(206)
                    byte_format = "bytes {0}-{1}/{2}"
                    byte_format = byte_format.format(lowbyte, \
                        highbyte, \
                        filelen)
                    self.send_header("Content-Range", byte_format)
                    self.send_header("Content-Length", str((highbyte - lowbyte) + 1))
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Accept-Ranges", "bytes")

                    self.end_headers()
                    with open(filename) as infile:
                        infile.seek(lowbyte)
                        try:
                            self.copyfile(infile, self.wfile)
                        except:
                            return
                elif fields[1] == "images" and ".." not in fields[2]:
                    filename = MEDIA_DIR + '/' + unquote(fields[2])

                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.end_headers()

                    imagefile = open(filename)
                    self.wfile.write(imagefile.read())


                elif fields[1] == "ink" and ".." not in fields[2]:
                    self.send_response(200)
                    if fields[2].split('/', 1)[0] == "css":
                        self.send_header("Content-type", "text/css")
                    elif fields[2].split('/', 1)[0] == "js":
                        self.send_header("Content-type", "text/javascript")
                    self.end_headers()

                    fields[2] = fields[2].rsplit('?', 1)[0]

                    inkfile = open("html_files/ink/" + fields[2]).read()

                    self.wfile.write(inkfile)


        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')

class ThreadedAuthedHTTPSServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass#yay for python


def serve_https(https_port=443, \
    HandlerClass=AuthHandler, \
    ServerClass=BaseHTTPServer.HTTPServer):
#    httpd = SocketServer.TCPServer(("", https_port), HandlerClass)
    httpd = ThreadedAuthedHTTPSServer(("", https_port), HandlerClass)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERTFILE_PATH, server_side=True)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."

    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "usage SimpleAuthServer.py [port] [password_file] [.pem file] [media_dir]"
        sys.exit()

    https_port = int(sys.argv[1])
#    key = base64.b64encode(sys.argv[2])
    keys = open(sys.argv[2]).read()
    keys = keys.split('\n')
    keys = map(None, keys)
    keys = filter(lambda x:':' in x, keys)
    keys = map(base64.b64encode, keys)
    keys = map(lambda x: "Basic {}".format(x), keys)
    CERTFILE_PATH = sys.argv[3]
    MEDIA_DIR = sys.argv[4]

    FILES = os.listdir(MEDIA_DIR)
    FILES = filter(lambda x: x[-4:] == ".mp4", FILES)
#    pprint(FILES)

    serve_https(https_port)


#    if len(sys.argv) == 4:
#        change_dir = sys.argv[3]
#        print "Changing dir to {cd}".format(cd=change_dir)
#        os.chdir(change_dir)


