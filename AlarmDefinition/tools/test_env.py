#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time


def command_timeout(cmd, timeout=60):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    t_beginning = time.time()
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
        time.sleep(0.1)
    return p.stdout.read()


if __name__ == '__main__':
    result = command_timeout(['/bin/sh', '-c', 'ls'])
    print result
