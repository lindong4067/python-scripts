#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import json
import sys
import esa_log as log


def get_watch_data():
    _data = sys.stdin.read()
    _data = json.loads(_data)
    return _data


def get_host_name():
    host_name = socket.gethostname()
    return host_name


def get_local_addr():
    my_name = socket.gethostname()
    my_addr = socket.gethostbyname(my_name)
    return my_addr


def get_host_list(_res):
    host_list = []
    for n in _res:
        host = n['Node']
        host_list.append(host)
    return host_list


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


def get_esa_master_status(local_host):
    _status = os.popen('esaclusterstatus').read()
    if _status is not None:
        this = _status.split('\n')
        if len(this) > 3:
            this = this[1]
            if ('M' in this) and (local_host in this) and ('(M)' not in this):
                return True
            else:
                return False


def restart_esa_service(service_name):
    return os.system('service %s restart' % service_name)


def is_om_running():
    om_status = get_esa_status('omcenter')
    if 'running' in om_status:
        return True
    else:
        return False


def main():
    log.logger.info('Run script : esa_state_handler.py')
    host_name = get_host_name()
    log.logger.info('Host name : %s' % host_name)
    om_running = is_om_running()
    log.logger.info('Is omcenter running : %s' % om_running)
    if not om_running:
        is_active_master = get_esa_master_status(host_name)
        log.logger.info('Is active ESA master : %s' % is_active_master)
        if is_active_master:
            rest = restart_esa_service('esama')
            log.logger.info('Restart ESA esama service : %s' % rest)
            rest = restart_esa_service('esafma')
            log.logger.info('Restart ESA esafma service : %s' % rest)
    log.logger.info('Finish script : esa_state_handler.py')


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
