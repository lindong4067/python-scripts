#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import sys


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


if __name__ == "__main__":
    try:
        re = command_timeout(cmd='/usr/local/bin/esaclusterstatus', timeout=20)
        print re
    except Exception, e:
        print e.message
        sys.exit(0)
