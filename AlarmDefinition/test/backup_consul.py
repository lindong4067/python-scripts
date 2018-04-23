#!/usr/bin/env python
# -*- coding: utf-8 -*-

import consul
import os

ALARM_DEFINITION_PATH_HW = '/opt/ESA/ESA/conf/fmAlarmDefinitions/hw_alarmdef.xml'
ALARM_DEFINITION_PATH_GMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_SMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_AECID = '/opt/ESA/ESA/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml'
CONSUL_KEY_HW_S = 'cm/values/18-smpc-cluster/datastorages/esaconfig/hw'
CONSUL_KEY_HW_G = 'cm/values/18-gmpc-cluster/datastorages/esaconfig/hw'
CONSUL_KEY_HW_A = 'cm/values/18-aecid-cluster/datastorages/esaconfig/hw'
CONSUL_KEY_GMPC = 'cm/values/18-gmpc-cluster/datastorages/esaconfig/gmpc'
CONSUL_KEY_SMPC = 'cm/values/18-smpc-cluster/datastorages/esaconfig/smpc'
CONSUL_KEY_AECID = 'cm/values/18-aecid-cluster/datastorages/esaconfig/aecid'


def exist_file(file_path):
    exist = os.path.exists(file_path)
    return exist


def read_file(file_path):
    rf = open(file_path, 'r')
    file_content = rf.read()
    rf.close()
    return file_content


if exist_file(ALARM_DEFINITION_PATH_HW):
    hw = read_file(ALARM_DEFINITION_PATH_HW)
    c = consul.Consul()
    c.kv.put(CONSUL_KEY_HW_S, hw)
    c.kv.put(CONSUL_KEY_HW_G, hw)
    c.kv.put(CONSUL_KEY_HW_A, hw)

if exist_file(ALARM_DEFINITION_PATH_GMPC):
    gmpc = read_file(ALARM_DEFINITION_PATH_GMPC)
    c = consul.Consul()
    c.kv.put(CONSUL_KEY_GMPC, gmpc)

if exist_file(ALARM_DEFINITION_PATH_SMPC):
    smpc = read_file(ALARM_DEFINITION_PATH_SMPC)
    c = consul.Consul()
    c.kv.put(CONSUL_KEY_SMPC, smpc)

if exist_file(ALARM_DEFINITION_PATH_AECID):
    aecid = read_file(ALARM_DEFINITION_PATH_AECID)
    c = consul.Consul()
    c.kv.put(CONSUL_KEY_AECID, aecid)
