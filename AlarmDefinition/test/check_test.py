#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

status = os.popen('service esafma status').read()
print status
if 'dead' in status:
    print False
if 'running' in status:
    print True
