#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import json
import base64

CHECK_FILE = '/opt-mpc/Config/template/config'
# CHECK_FILE = 'C:/Temp/out/config'
CONSUL_KEY_SMPC = 'esa/cluster/config/smpc'
ALARM_DEFINITION_PATH = '/opt/ESA/ESA/conf/fmAlarmDefinitions'
# ALARM_DEFINITION_PATH = 'C:/Temp/out'


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


ex = os.path.isfile(CHECK_FILE)
if ex:
    file_c = read_file(CHECK_FILE)
    if 'PRODUCT_NAME=smpc' in file_c:
        request = urllib2.Request('http://localhost:8500/v1/kv/' + CONSUL_KEY_SMPC)
        response = urllib2.urlopen(request)
        res = response.read()
        _res = json.loads(res)
        if _res:
            _res_value = base64.b64decode(_res[0]['Value'])
            print _res_value
            file_path = ALARM_DEFINITION_PATH + '/SMPC_alarmdefinition.xml'
            save_to_file(file_path, _res_value)
