#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import consul

CHECK_FILE = '/opt-mpc/Config/template/config'
# CHECK_FILE = 'C:/Temp/out/config'
CONSUL_KEY_GMPC = 'esa/cluster/config/smpc'
ALARM_DEFINITION_PATH = '/opt/ESA/ESA/conf/fmAlarmDefinitions'
# ALARM_DEFINITION_PATH = 'C:/Temp/out'


def read_file(file_path):
    rf = open(file_path, 'r')
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
        c = consul.Consul()
        index, data = c.kv.get(CONSUL_KEY_GMPC)
        if data is not None:
            xml = data['Value']
            file_na = ALARM_DEFINITION_PATH + '/SMPC_alarmdefinition.xml'
            save_to_file(file_na, xml)
