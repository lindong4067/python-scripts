#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket


def get_esa_status(service_name):
    status = os.popen('service %s status' % service_name).read()
    return status


def start_esa_service(status, service_name):
    if 'dead' in status:
        os.popen('service %s start' % service_name)


def stop_esa_service(status, service_name):
    if 'running' in status:
        os.popen('service %s stop' % service_name)


def restart_esa_service(service_name):
    os.popen('service %s restart' % service_name)


def get_local_ip():
    host_name = socket.gethostname()
    host_address = socket.gethostbyname(host_name)
    return host_address


def get_esa_master_status(status):
    if 'running' in status:
        _status = os.popen('esaclusterstatus').read()
        this = _status.split('\n')[1]
        local_host = get_local_ip()
        if 'M' in this and local_host in this:
            print True
        else:
            print False


def main():
    esama_status = get_esa_status('esama')
    start_esa_service(esama_status, 'esama')
    esafma_status = get_esa_status('esafma')
    start_esa_service(esafma_status, 'esafma')
    esapma_status = get_esa_status('esapma')
    start_esa_service(esapma_status, 'esapma')


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
