#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

a = 1


def fun_timer():
    global a
    a += 1
    print 'Hello World!{}'.format(a)
    global timer
    timer = threading.Timer(5.5, fun_timer)
    timer.start()


thread = threading.Timer(1, fun_timer)
thread.start()
