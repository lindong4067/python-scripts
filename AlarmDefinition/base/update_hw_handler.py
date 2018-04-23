#!/usr/bin/env python
# -*- coding: utf-8 -*-

import consul

CONSUL_KEY_HW = 'esa/cluster/config/hw'
ALARM_DEFINITION_PATH = '/opt/ESA/ESA/conf/fmAlarmDefinitions'
# ALARM_DEFINITION_PATH = 'C:/Temp/out'


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


c = consul.Consul()
index, data = c.kv.get(CONSUL_KEY_HW)
if data is not None:
    xml = data['Value']
    file_path = ALARM_DEFINITION_PATH + '/hw_alarmdef.xml'
    save_to_file(file_path, xml)
