#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import base64

ALARM_DEFINITION_PATH_HW = '/opt/ESA/ESA/conf/fmAlarmDefinitions/hw_alarmdef.xml'
ALARM_DEFINITION_PATH_GMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_SMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_AECID = '/opt/ESA/ESA/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml'


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
    if 'gmpc' in _key:
        file_path = ALARM_DEFINITION_PATH_GMPC
    elif 'smpc' in _key:
        file_path = ALARM_DEFINITION_PATH_SMPC
    elif 'aecid' in _key:
        file_path = ALARM_DEFINITION_PATH_AECID
    elif 'hw' in _key:
        file_path = ALARM_DEFINITION_PATH_HW
    return file_path


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


def main():
    data = get_watch_data()
    key = get_consul_key(data)
    value = get_consul_value(data)
    file_path = get_file_path(key)
    if file_path is not None:
        save_to_file(file_path, value)


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
        sys.exit(1)
