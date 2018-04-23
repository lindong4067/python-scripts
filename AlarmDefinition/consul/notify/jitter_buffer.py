#!/usr/bin/env python
#--coding:utf-8--

import time, threading
from utils import *

class JitterBuffer(object):
    ''' JitterBuffer '''

    def __init__(self):
        ''' new empty JitterBuffer '''
        self.lock = threading.Lock()
        self.buffer = []

    def _lock(self):
        ''' Lock JitterBuffer '''
        self.lock.acquire();

    def _unlock(self):
        ''' Unlock JitterBuffer '''
        self.lock.release();

    def pop_all(self):
        ''' remove and return all items. '''
        self._lock()

        data = self.buffer;
        self.buffer = []

        self._unlock()
        return data;

    def push(self, data):
        ''' append object to end '''
        self._lock()
        if type(data) == type([]) or type(data) == type((0,)):
            self.buffer.extend(data);
        if type(data) == type({}):
            self.buffer.append(data)
        self._unlock()
        return 0;

