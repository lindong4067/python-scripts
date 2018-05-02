#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
str2 = ''
str2 += 'ABC'

str2 = str2[:-1]
url = 'http://{}:{}/v1/agent/members'.format('localhost', 8500)
print url


def return_test():
    x = '123'
    y = 123
    return x, y


_res = return_test()

a = _res[0]
# print isinstance(a, str)
b = _res[1]
# print isinstance(b, int)

strs = {'a': '123', 'b': '234', 'c': '345'}

pwd = os.system('dir')

size = '   234 = game   '.strip().split('=')
# print 'size : %s' % size[1].strip()

ip_port = ('local', 8500)
print 'http://%s:%s/v1/kv/%s' % (ip_port[0],ip_port[1], 'consul_key')

if ('smpc' == 'hw') or ('smpc' == 'smpc'):
    print True
else:
    print False

print '********'
if None:
    print 'None'
js = json.loads('{"2":"3","3":"4"}')
print js
