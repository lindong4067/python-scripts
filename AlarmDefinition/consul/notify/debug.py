#!/usr/bin/env python
#--coding:utf-8--

import os, sys
import traceback
import time

class Debug():
    ''' Debug '''
    debug_flags = {}                    # debug flags
    __logfile = ""                      # filename of log file
    __logf = None                       # log file fd
    __log2stdout = True                 # log to stdout or not

    ''' init Debug '''
    def __init__(self):
        pass

    ''' init Debug '''
    @staticmethod
    def config(logfile="", log2stdout=True, maxsize=0, logcheck=10):
        #Debug.notice("log2stdout: {0}".format(log2stdout))
        try:
            Debug.__logfile = logfile
            Debug.__log2stdout = log2stdout

            # open() with paramter 'a' other than 'w' to avoid log be cleared
            Debug.__logf = open(Debug.__logfile, "a")
        except Exception as err:
            print("Open logfile %s error: %s" % (Debug.__logfile, err))
        return Debug.__logf

    @staticmethod
    def init_debug(key, onoff=False):
        Debug.debug_flags[key] = bool(onoff)

    @staticmethod
    def set_debug(key, onoff=True):
        ''' turns on/off the debug flag '''
        if 'all' == key:
            for flag in Debug.debug_flags.keys():
                Debug.debug_flags[flag] = bool(onoff)
        elif key in Debug.debug_flags.keys():
            Debug.debug_flags[key] = bool(onoff)

    @staticmethod
    def get_debug(key):
        ''' turns on/off debug flag '''
        if key in Debug.debug_flags.keys():
            return Debug.debug_flags[key]
        return False;

    @staticmethod
    def get_debugs(key = ""):
        ''' get debug flags '''
        return Debug.debug_flags;

    @staticmethod
    def _write(msg):
        # write to logfile
        if Debug.__logf:
            Debug.__logf.write(str(msg) + "\n")
            Debug.__logf.flush()
        if Debug.__log2stdout:
            print(msg)

    @staticmethod
    def debug(msg):
        Debug._write("%s [DEBUG] %s" % (time.ctime(), msg))

    @staticmethod
    def warn(msg):
        Debug._write("%s [WARNING] %s" % (time.ctime(), msg))

    @staticmethod
    def notice(msg):
        Debug._write("%s [NOTICE] %s" % (time.ctime(), msg))

    @staticmethod
    def error(msg):
        Debug._write("%s [ERROR] %s" % (time.ctime(), msg))

    @staticmethod
    def fatal(msg):
        Debug._write("%s [FATAL] %s\nTraceback: %s" %
              (time.ctime(), str(msg), traceback.format_exc()))
