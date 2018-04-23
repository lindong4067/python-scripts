#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import urllib2
import os
import json

local_name = socket.gethostname()
local_host = socket.gethostbyname(local_name)
request = urllib2.Request('http://localhost:8500/v1/health/service/db-uda-udaserver')
response = urllib2.urlopen(request)
res = response.read()
_res = json.loads(res)

_address_list = []
for r in _res:
        _address = r['Node']['Address']
        _address_list.append(_address)

if local_host not in _address_list:
    status = os.popen('service esama status').read()
    if 'running' in status:
        os.popen('service esama stop')
    status = os.popen('service esafma status').read()
    if 'running' in status:
        os.popen('service esafma stop')
    status = os.popen('service esapma status').read()
    if 'running' in status:
        os.popen('service esapma stop')

if local_host in _address_list:
    status = os.popen('service esama status').read()
    if 'dead' in status:
        os.popen('service esama start')
    status = os.popen('service esafma status').read()
    if 'dead' in status:
        os.popen('service esafma start')
    status = os.popen('service esapma status').read()
    if 'dead' in status:
        os.popen('service esapma start')
