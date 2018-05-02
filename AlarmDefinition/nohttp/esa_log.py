#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

logger = logging.getLogger('esa-state')

formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

file_handler = logging.FileHandler('/opt/consul/script/esaconfig/esa-state.log')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

