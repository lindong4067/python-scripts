#!/usr/bin/env python
# -*- coding: utf-8 -*-

import consul

c = consul.Consul()
c.kv.put('foo', 'sar')
