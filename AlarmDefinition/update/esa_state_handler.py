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


def get_address_list(_res):
    address_list = []
    for n in _res:
        address = n['Node']['Address']
        address_list.append(address)
    return address_list


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


def start_esa():
    start_esa_server('esama')
    start_esa_server('esafma')
    start_esa_server('esapma')


def stop_esa():
    stop_esa_server('esama')
    stop_esa_server('esafma')
    stop_esa_server('esapma')


def main():
    data = get_watch_data()
    addresses = get_address_list(data)
    local_host = get_local_addr()
    # if local_host not in addresses and len(addresses) > 1:
    if local_host not in addresses:
        stop_esa()
    if local_host in addresses:
        start_esa()


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
