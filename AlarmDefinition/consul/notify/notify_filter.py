#!/usr/bin/env python
# --coding:utf-8--

import time
from jitter_buffer import JitterBuffer
from notifier import Notifier
from diff_manager import DiffManager
from notify_httpd import NotifyHttpServer
from health_check import ServiceRegisterThread
from utils import *


class NotifyFilter(object):
    ''' NotifyFilter '''

    def __init__(self):
        pass

    @staticmethod
    def run(httpd_ip, httpd_port):
        # 1) create JitterBuffer
        Debug.notice("Create JitterBuffer ...")
        jtbuf = JitterBuffer()

        # 2) start Notifier thread
        Debug.notice("Create Notifier ...")
        notifier = Notifier(jtbuf)
        notifier.start();

        # 3) create DiffManager
        Debug.notice("create DiffManager ...")
        diff_manager = DiffManager(jtbuf)
        NotifyHttpServer.user_ctx = diff_manager;

        # 4) create & start httpserver
        httpd = NotifyHttpServer(httpd_ip, httpd_port)
        httpd.run_forever()


def main(bldaemon=False):
    while True:
        try:
            # 0) Init debug & log
            logfile = get_notify_data_path() + "/notify_filter.log"
            Debug.config(logfile, log2stdout=(not bldaemon))
            Debug.set_debug("all", False)

            # 1) Log Process ID
            pid_file = get_notify_data_path() + "/PID_notify_filter"
            cmdstr = "echo " + str(os.getpid()) + " > " + pid_file
            Debug.notice("PID: %s" % pid_file)
            os.system(cmdstr)

            # start service register thread
            service_register = ServiceRegisterThread()
            service_register.start()

            # 2) Aplication main '''
            Debug.notice("Hostname: %s" % get_hostname())
            httpd_ip, httpd_port = get_filter_httpd_address()
            NotifyFilter.run(httpd_ip, httpd_port)
        except:
            Debug.fatal("NotifyFilter failed: %s" % str(sys.exc_info()))
            time.sleep(1)
        return False
