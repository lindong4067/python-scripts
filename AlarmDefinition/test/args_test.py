#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def test():
    args = sys.argv
    args_len = len(args)
    if args_len == 1:
        print 'Hello World!'
    elif args_len == 2:
        print 'Hello %s!' % args[1]
    else:
        print 'Too many parameters!'


if __name__ == '__main__':
    test()
