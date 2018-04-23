#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

# 获取logger实例，参数为空返回root logger
logger = logging.getLogger('esa-state')

# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# 文件日志
file_handler = logging.FileHandler('esa-state.log')
# 指定输出格式 set方式
file_handler.setFormatter(formatter)

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
# 直接给formatter赋值
console_handler.formatter = formatter

# 为logger添加的日志处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 指定日志的最低输出级别
logger.setLevel(logging.INFO)

# 输出不同级别的log
# logger.debug('This is debug info.')
# logger.info('This is information.')
# logger.warn('This is warning message.')
# logger.error('This is error message.')
# logger.fatal('this is fatal message, it is same as logger.critical.')
# logger.critical('this is critical message.')
