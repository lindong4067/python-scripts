#!/usr/bin/env python
# -*- coding: utf-8 -*-

import consul

CONSUL_KEY_HW = 'esa/cluster/config/hw'
ALARM_DEFINITION_PATH = 'C:\\Temp\\out'
c = consul.Consul()
index, data = c.kv.get(CONSUL_KEY_HW)
print data['Value']
# fo = open(ALARM_DEFINITION_PATH + 'hw_alarmdef.xml', 'w')
# fo.write(data['Value'])
# fo.close