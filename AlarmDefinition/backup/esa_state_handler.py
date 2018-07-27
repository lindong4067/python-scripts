#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import subprocess
import esa_log as log


def main():
    log.logger.info('Run script : esa_state_handler.py')
    host_name = socket.gethostname()
    log.logger.info('Host name : %s' % host_name)
    res = subprocess.Popen('esaclusterstatus', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    status = res.stdout.read()
    res.stdout.close()
    log.logger.info('Get ESA status : %s' % status)
    if 'Cluster mode inactive or cluster not started yet' in status:
        restart = os.system('service esa_ma restart')
        log.logger.info('Restart ESA esa_ma service : %s' % restart)
        restart = os.system('service esa_fma restart')
        log.logger.info('Restart ESA esa_fma service : %s' % restart)
    elif 'ERROR Could not connect to FM Agent: //127.0.0.1:8666/Cluster' in status:
        source = os.system('source /opt/consul/script/env/consul.export')
        log.logger.info('Source Consul Env : %s' % source)
        load = os.system('consul reload')
        log.logger.info('Consul Reload : %s' % load)
        restart = os.system('service esa_ma restart')
        log.logger.info('Restart ESA esa_ma service : %s' % restart)
        restart = os.system('service esa_fma restart')
        log.logger.info('Restart ESA esa_fma service : %s' % restart)
    elif 'Cluster members' in status:
        lens = status.split('\n')
        log.logger.info('Get ESA status list : %s' % lens)
        if len(lens) >= 2:
            len2 = lens[1]
            log.logger.info('Yes! ESA status line2 : %s' % len2)
            if ('M' in len2) and (host_name in len2) and ('(M)' not in len2):
                log.logger.info('ESA master is active : %s' % host_name)
                om_status = os.popen('service omcenter status').read()
                if 'Active: active (running)' not in om_status:
                    log.logger.info('OMCenter is not running : %s' % host_name)
                    restart = os.system('service esa_ma restart')
                    log.logger.info('Restart ESA esa_ma service : %s' % restart)
                    restart = os.system('service esa_fma restart')
                    log.logger.info('Restart ESA esa_fma service : %s' % restart)
                else:
                    log.logger.info('OMCenter is running : %s' % host_name)
            elif ('M' not in len2) and (host_name in len2) and (len(lens) == 3):
                log.logger.info('ESA agent is islanding : %s' % host_name)
                restart = os.system('service esa_ma restart')
                log.logger.info('Restart ESA esa_ma service : %s' % restart)
                restart = os.system('service esa_fma restart')
                log.logger.info('Restart ESA esa_fma service : %s' % restart)
    log.logger.info('Finish script : esa_state_handler.py')


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        log.logger.error(e.message)
        print e.message
