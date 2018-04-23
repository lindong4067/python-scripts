#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import esa_log as log


def service_status(name):
    status = os.popen('service %s status' % name).read()
    if 'running' in status:
        return True
    elif 'dead' in status:
        return False


def start_service(name):
    os.system('service %s start' % name)


def stop_service(name):
    os.system('service %s stop' % name)


if __name__ == '__main__':
    log.logger.info('***************************************************')
    log.logger.info('******************** Auto Test Start **************')
    log.logger.info('***************************************************')
    status = service_status('omcenter')
    if status:
        stop_service('omcenter')
        log.logger.info('OM Center Status : %s' % status)
        log.logger.info('Stop OM Center Service...')
    else:
        start_service('omcenter')
        log.logger.info('OM Center Status : %s' % status)
        log.logger.info('Start OM Center Service...')
    log.logger.info('***************************************************')
    log.logger.info('******************** Auto Test Finish *************')
    log.logger.info('***************************************************')
