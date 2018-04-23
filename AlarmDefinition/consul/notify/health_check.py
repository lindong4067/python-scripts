#!/usr/bin/env python
# --coding:utf-8--


import sys, os
import re
import time, threading
from debug import Debug
from utils import *
from fds_health_check import FdsService


class ServiceRegisterThread(threading.Thread):
    ''' ServiceRegister '''

    def __init__(self):
        # init thread
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        ''' register fds service, 
            if failed sleep a while and then try again
        '''
        while True:
            # register fds service
            if fds_service_register():
                Debug.notice("fds service register success!")
                break
            time.sleep(15)
        return True


def fds_service_register():
    ''' register fds service to consul
        return True is success, otherwise False
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    script_file = current_dir + "/health_check.py"

    fds = FdsService(script_file)
    fds.register_fdsserver()

    return fds.service_is_registered()


def fds_service_health_check():
    ''' do health check for fds service
        returns:
            0     - passing
            1     - warning
            other - critical
    '''
    fds = FdsService(os.path.realpath(__file__))
    return fds.service_health_check()


if __name__ == '__main__':
    ''' health script main '''
    logfile = get_notify_data_path() + "/health_check.log"
    Debug.config(logfile, log2stdout=True, logcheck=1)

    # When CONSUL_IP can't get from environ, get it from config file
    # and update to environ
    if not "CONSUL_IP" in os.environ.keys():
        reqcmd = '''
            cat /var/opt/setup/site.export | egrep '^CONSUL_IP=.*$' | \
            awk -F= '{ print $2 }'
        '''
        resp = os.popen(reqcmd, "r").read()
        if resp:
            resp = resp.strip('"\n')
            os.environ["CONSUL_IP"] = resp
        print("CONSUL_IP: %s" % str(resp))

    state = fds_service_health_check()
    print("fds-service state: %d" % state)
    sys.exit(state)
