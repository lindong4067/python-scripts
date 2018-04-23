#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

path = os.path.realpath(__file__)

path = os.path.dirname(os.path.realpath(__file__))
# 把当前文件所在的文件夹添加到环境变量
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# 获取执行脚本的参数列表
args = sys.argv

le = len(sys.argv)
# 直接执行comm命令
s = os.system('dir')

