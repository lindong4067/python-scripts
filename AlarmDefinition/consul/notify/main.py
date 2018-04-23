#!/usr/bin/env python
# --coding:utf-8--


import os
import sys
import notify_filter

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def main(_bldaemon=False):
    if not _bldaemon:
        ''' run as normal application '''
        notify_filter.main(_bldaemon)
    else:
        ''' run as daemon '''
        import daemon
        with daemon.DaemonContext():
            notify_filter.main(_bldaemon)


if __name__ == '__main__':
    # -D run as daemon
    _bldaemon = False
    if len(sys.argv) >= 2 and sys.argv[1] == "-D":
        _bldaemon = True

    # application main
    main(_bldaemon)
