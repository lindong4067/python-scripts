#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
import base64
import esa_log as log

ALARM_DEFINITION_PATH_HW = '/opt/ESA/ESA/conf/fmAlarmDefinitions/hw_alarmdef.xml'
ALARM_DEFINITION_PATH_GMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_SMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_AECID = '/opt/ESA/ESA/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml'
CHECK_FILE = '/var/opt/setup/site.export'


def get_watch_data():
    data = sys.stdin.read()
    data = json.loads(data)
    return data


def get_consul_key(_data):
    key = _data['Key']
    return key


def get_consul_value(_data):
    value = _data['Value']
    value = base64.b64decode(value)
    return value


def get_file_path(_key):
    file_path = None
    if 'esaconfig/gmpc' in _key:
        file_path = ALARM_DEFINITION_PATH_GMPC
    elif 'esaconfig/smpc' in _key:
        file_path = ALARM_DEFINITION_PATH_SMPC
    elif 'esaconfig/aecid' in _key:
        file_path = ALARM_DEFINITION_PATH_AECID
    elif 'esaconfig/hw' in _key:
        file_path = ALARM_DEFINITION_PATH_HW
    return file_path


def read_file(_file_path):
    rf = open(_file_path, 'r')
    file_content = rf.read()
    rf.close()
    return file_content


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


def get_machine_type_by_config(config):
    if os.path.isfile(config):
        file_c = read_file(config)
        if 'PRODUCT_NAME=gmpc' in file_c:
            return 'gmpc'
        elif 'PRODUCT_NAME=aecid' in file_c:
            return 'aecid'
        elif 'PRODUCT_NAME=smpc' in file_c:
            return 'smpc'


def get_definition_type_by_key(_key):
    if 'esaconfig/gmpc' in _key:
        return 'gmpc'
    elif 'esaconfig/smpc' in _key:
        return 'smpc'
    elif 'esaconfig/aecid' in _key:
        return 'aecid'
    elif 'esaconfig/hw' in _key:
        return 'hw'


def main():
    log.logger.info('Run script : %s' % 'update_alarm_handler.py')
    data = get_watch_data()
    log.logger.info('Get watch data : %s' % data)
    key = get_consul_key(data)
    log.logger.info('Get consul key from data : %s' % key)
    definition_type = get_definition_type_by_key(key)
    log.logger.info('Get definition type by key : %s' % definition_type)
    machine_type = get_machine_type_by_config(CHECK_FILE)
    log.logger.info('Get machine type by key : %s' % machine_type)
    if definition_type == 'hw' or definition_type == machine_type:
        value = get_consul_value(data)
        log.logger.info('Get consul value from data : %s' % value)
        file_path = get_file_path(key)
        log.logger.info('Get file path by key : %s' % file_path)
        if file_path is not None and value is not None:
            save_to_file(file_path, value)
            log.logger.info('Save to file : %s' % file_path)
    log.logger.info('Finish script : %s' % 'update_alarm_handler.py')


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
        sys.exit(1)
