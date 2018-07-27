#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def check_args():
    args = sys.argv
    args_len = len(args)
    error_mess = 'Only such parameters are legal: 1. -r, 2. -c.'
    if args_len == 2:
        m1 = ' Run Alarm Test Tool '.center(50, "=")
        arg = args[1]
        if arg == '-r':
            m2 = ' Send All Alarms Specified '.center(50, "=")
            print m1, '\n', m2
            return True
        elif arg == '-c':
            m3 = ' Clear All Alarms Specified '.center(50, "=")
            print m1, '\n', m3
            return True
        else:
            print error_mess
            return False
    else:
        print error_mess
        return False


def read_alarm_specified():
    alarm_file = open("alarm_test_tool.txt")
    for line in alarm_file:
        print line
    alarm_file.close()
    pass


def send_alarm():
    read_alarm_specified()
    pass


def clear_alarm():
    read_alarm_specified()
    pass


if __name__ == '__main__':
    check_result = check_args()
    if check_result:
        arg_01 = sys.argv[1]
        if arg_01 == '-r':
            send_alarm()
        else:
            clear_alarm()
