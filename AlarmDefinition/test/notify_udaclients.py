#!/usr/bin/env python

import os
import sys
import json
import socket
import urllib2
import logging
from logging.handlers import RotatingFileHandler


class ConsulNotify(object):
    my_dir = os.path.split(os.path.realpath(__file__))[0] + '/../'
    consul_logfile = my_dir + 'logs/consul.log'
    rt_handler = RotatingFileHandler(consul_logfile, maxBytes=10 * 1024 * 1024, backupCount=1)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s')
    rt_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(rt_handler)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s'))
    logging.getLogger('').addHandler(console)
    Logger = logging.getLogger('udaclient')
    Logger.setLevel(logging.INFO)

    def __init__(self, server_url, client_url):
        self.myHostname = socket.gethostname()
        self.serverUrl = server_url
        self.clientUrl = client_url
        self.clientList = list()
        self.Logger.info('notify service ...')

    def notify(self):
        server_svc = self.getServices(self.serverUrl)
        client_svc = self.getServices(self.clientUrl)
        self.setClientList(client_svc)
        self.sendToClientsByHTTP2(server_svc)

    def getServices(self, url):
        req = urllib2.Request(url=url)
        resp = urllib2.urlopen(req)
        return resp.read()

    def setClientList(self, clientSvc):
        try:
            clients = json.loads(clientSvc)
        except ValueError, e:
            self.Logger.error("json decode error, {0}".format(e))
            sys.exit(1)

        for client in clients:
            if client['Node']['Node'] == self.myHostname:
                self.clientList.append({'ip': client['Service']['Address'], 'port': client['Service']['Port']})
        self.Logger.info('notify clients ... {0}'.format(self.clientList))

    def sendToClientsByTCP(self, data):
        if len(self.clientList) == 0:
            self.Logger.error('No passing client services')
            sys.exit(1)
        for client in self.clientList:
            host = client['ip']
            port = client['port']
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
                s.connect((host, port))
            except socket.error, arg:
                (errno, err_msg) = arg
                self.Logger.error("connect server failed: {0}, error no = {1}".format(err_msg, errno))
                s.close()
                continue
            s.send(data)
            self.Logger.info("SEND MSG [{0}:{1}] [{2}]".format(host, port, data))
            try:
                recvResp = s.recv(1024)
            except socket.timeout as e:
                self.Logger.error("RECV MSG [{0}]".format(e))
                s.close()
                continue
            self.Logger.info("RECV MSG [{0}:{1}] [{2}]".format(host, port, recvResp))
            s.close()

    def sendToClientsByHTTP2(self, data):
        SvcFileName = self.my_dir + 'logs/services.json'
        serverSvcFile = open(SvcFileName, 'w')
        serverSvcFile.write(data)
        serverSvcFile.close()

        if len(self.clientList) == 0:
            self.Logger.error('No passing client services')
            sys.exit(1)
        for client in self.clientList:
            host = client['ip']
            port = client['port']
            cmd = "/opt/curl_http2/bin/nghttp http://{0}:{1}/watch -H':method: PUT' -d'{2}'".format(host, port,
                                                                                                    SvcFileName)
            output = os.popen(cmd)
            self.Logger.info("SEND MSG [{0}:{1}] [{2}]".format(host, port, data))
            self.Logger.info("RESULT {0}".format(output.read()))


def install_3pp():
    if not os.path.exists("/opt/curl_http2/bin/nghttp"):
        os.system("zypper in -y curl_http2")


def main():
    passingServerUrl = "http://localhost:8500/v1/health/service/db-uda-udaserver?passing"
    passingClientUrl = "http://localhost:8500/v1/health/service/db_uda-udaclient?passing"

    install_3pp()
    consul = ConsulNotify(passingServerUrl, passingClientUrl)
    consul.notify()


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print str(e)
        sys.exit(1)
