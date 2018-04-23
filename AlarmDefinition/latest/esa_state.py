#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import json
import sys


def get_watch_data():
    _data = sys.stdin.read()
    _data = json.loads(_data)
    return _data


def get_local_addr():
    my_name = socket.gethostname()
    my_addr = socket.gethostbyname(my_name)
    return my_addr


def get_esa_status(server_name):
    status = os.popen('service {} status'.format(server_name)).read()
    return status


def start_esa_server(server_name):
    status = get_esa_status(server_name)
    if 'dead' in status:
        os.popen('service {} start'.format(server_name))


def stop_esa_server(server_name):
    status = get_esa_status(server_name)
    if 'running' in status:
        os.popen('service {} stop'.format(server_name))


def get_esa_master_status():
    _status = os.popen('esaclusterstatus').read()
    this = _status.split('\n')[1]
    local_host = get_local_addr()
    if 'M' in this and local_host in this:
        return True
    else:
        return False


def restart_esa_service(service_name):
    os.popen('service %s restart' % service_name)


def main():
    om_status = get_esa_status('omcenter')
    if 'dead' in om_status:
        is_active = get_esa_master_status()
        if is_active:
            restart_esa_service('esama')


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
