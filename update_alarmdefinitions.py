#!/usr/bin/env python

import logging
import sys
import consul

ALARM_DEFINITION_PATH = 'C:\\Temp\\out\\'
# ALARM_DEFINITION_PATH = '/opt/ESA/ESA/conf/fmAlarmDefinitions'
CONSUL_KEY_SMPC = 'esa/cluster/config/smpc'
CONSUL_KEY_GMPC = 'esa/cluster/config/gmpc'
CONSUL_KEY_HW = 'esa/cluster/config/hw'


# def save_to_file(file_name, str):
#     fw = open(file_name, 'W')
    # fh = open(file_name, 'w')
    # fh.write(str)
    # fh.close()


c = consul.Consul()
index, data = c.kv.get(CONSUL_KEY_GMPC)

if data is not None:
    gmpc = data['Value']
    # file = ALARM_DEFINITION_PATH + 'GMPC_alarmdefinition.xml'
    # save_to_file(file, gmpc)
    print(gmpc)
