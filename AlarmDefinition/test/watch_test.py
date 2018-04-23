#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

data = sys.stdin.read()
print data
fw = open('/opt/consul/scripts/log.txt', 'a+')
fw.write(data)
fw.close()
