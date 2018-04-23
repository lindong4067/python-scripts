#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


def get_argv():
    args = sys.argv
    return args


# save_to_file('C:\Temp\out\test.txt', 'linux-kiwi-31')
_args = get_argv()
_len = len(_args)
print _len
print _args[0]
