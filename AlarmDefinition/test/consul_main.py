#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import notify_filter

def main(bldaemon=False):
    ''' run as normal application '''
    if not bldaemon:
        notify_filter.main(bldaemon = bldaemon)
    else:
        ''' run as daemon '''
        import daemon
        with daemon.DaemonContext():
            notify_filter.main(bldaemon)

if __name__ == '__main__':
    # -D run as daemon
    bldaemon = False
    if (len(sys.argv) >= 2 and sys.argv[1] == "-D"):
        bldaemon = True

    # application main
    main(bldaemon)