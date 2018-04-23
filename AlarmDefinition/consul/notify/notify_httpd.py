#!/usr/bin/env python
#--coding:utf-8--

import json, sys
from diff_manager import DiffManager
from utils import *

''' debug purpose '''
module_name = "notify_httpd";
Debug.init_debug(module_name)

class NotifyHttpServer_RequestHandler(BaseHTTPRequestHandler):
    ''' NotifyHttpServer RequestHandler '''
    # GET
    def do_GET(self):
        ''' OAM interface '''
        if not self.path.startswith("/oam/"):
            return
        path = self.path.strip('/')
        path = path.split('/');

        ''' set debug flags: /oam/debug/{debug_flag}/{0|1} '''
        if len(path) >= 2 and 'debug' == path[1]:
            if len(path) >= 4:
                Debug.set_debug(path[2], getint(path[3]));
            resp = Debug.get_debugs()
        else:
            resp = "Bad request: " + self.path
        self.json_response(200, resp)

    def json_response(self, retcode, desc):
        ''' http response '''
        resp = {"result": retcode, "desc": desc}
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(json_dumps4(resp).encode("UTF-8"))

    def http_response(self, retcode, desc):
        ''' http response '''
        self.send_response(retcode)
        self.end_headers()

    def filter_request_handle(self, jdata):
        ''' request_handle: put data to diff_manager '''
        try:
            diff_manager = NotifyHttpServer.user_ctx;
            if type(diff_manager) != DiffManager:
                Debug.error("Error: Bad diff_manager type: %s" % type(diff_manager))
                return False
            diff_manager.set_new_data(jdata);
            return True
        except Exception as err:
            Debug.fatal("Error: %s" % (err))

    def handle_watch_data(self):
        data = self.rfile.read(int(self.headers['content-length'])).decode("UTF-8")
        Debug.notice("httpd raw input(len: %d): %.35s" % (len(data), data))

        jdata = json_parse(data);
        if Debug.get_debug(module_name):
            Debug.debug("input data: %s" % json.dumps(jdata, indent=4))
        self.filter_request_handle(jdata)
        self.http_response(200, "OK")

    def do_POST(self):
        self.do_PUT()
    def do_PUT(self):
        ''' http put command '''
        if self.headers['content-type'] != 'application/json':
            return self.http_response(400, "Bad Request")
        if Debug.get_debug(module_name):
            Debug.debug("Path: %s" % self.path)

        # route request by path
        if (self.path == "/watch_data"):
            return self.handle_watch_data()
        return self.http_response(404, "Not Found")

class NotifyHttpServer(object):
    ''' NotifyHttpServer '''
    user_ctx = None
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port;

    def run_forever(self):
        ''' start http server '''
        # Server settings
        server_address = (self.ip, self.port)
        httpd = HTTPServer(server_address, NotifyHttpServer_RequestHandler)

        Debug.notice('NotifyHttpServer server: %s:%u' % (self.ip, self.port))
        Debug.notice('running server...')
        httpd.serve_forever()

