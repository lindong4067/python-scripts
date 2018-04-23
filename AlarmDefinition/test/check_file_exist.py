#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

logging.info('debug message')

# 校验文件是否存在(1)
ex = os.path.exists('C:\\Temp\\out\\test.txt')
# print ex
ex = os.path.exists('C:/Temp/out/t.txt')
# print ex
# 只校验文件，忽略文件夹
ex = os.path.isfile('C:\\Temp\\out\\test.txt')
# print ex
_file = os.path.realpath(__file__)
print _file
_file = os.path.split(os.path.realpath(__file__))[0]
print _file

