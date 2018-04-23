#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import base64

CONSUL_KEY_HW = 'esa/cluster/config/hw'
ALARM_DEFINITION_PATH = '/opt/ESA/ESA/conf/fmAlarmDefinitions'
# ALARM_DEFINITION_PATH = 'C:/Temp/out'


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


request = urllib2.Request('http://localhost:8500/v1/kv/' + CONSUL_KEY_HW)
response = urllib2.urlopen(request)
res = response.read()
_res = json.loads(res)
if _res:
    _res_value = base64.b64decode(_res[0]['Value'])
    print _res_value
    file_path = ALARM_DEFINITION_PATH + '/hw_alarmdef.xml'
    save_to_file(file_path, _res_value)
