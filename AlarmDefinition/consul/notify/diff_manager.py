#!/usr/bin/env python
#--coding:utf-8--

import json, sys
from utils import *
from jitter_buffer import JitterBuffer
from diff_component import DiffComponent
from diff_system import DiffSystem
from diff_datastorages import DiffDatastorages
''' debug purpose '''
module_name = "diff_manager";
Debug.init_debug(module_name)

class DiffManager(object):
    ''' DiffManager '''
    def __init__(self, jtbuf):
        # create & initialize differ instance
        diff_component   = DiffComponent(jtbuf)
        diff_datastorage = DiffDatastorages(jtbuf)
        diff_system = None # aecid has no System
        if get_productname() != "aecid":
            diff_system  = DiffSystem(jtbuf)
        self.differ_list = {
            "components":   diff_component,
            "system":       diff_system,
            "datastorages": diff_datastorage
        }
        Debug.notice("notifier_list: %s" % str(self.differ_list))

    def __data_sanity_check(self, jdata):
        ''' basic check '''
        if not type(jdata) is type([]):
            Debug.error("Bad input data type, required []: %s" % type(jdata))
            return False
        for it in jdata:
            if not type(it) is type({}):
                Debug.error("Bad input data type, required {}:" % type(it))
                return False;
            for key in ("Key", "ModifyIndex", "Value"):
                if not key in it.keys():
                    Debug.error("Bad input data with keys: %s." % it.keys())
                    return False
        return True

    def __get_differ_instance(self, jdata):
        ''' basic check '''
        if not jdata[0] or not jdata[0]["Key"]:
            return None

        # cm/values/1.0/components/
        keys = jdata[0]["Key"].split("/")
        if keys and len(keys) < 4:
            return None

        # find instance
        inst_name = keys[3]
        if not keys[3] in self.differ_list.keys():
            return None
        return self.differ_list[inst_name]

    def set_new_data(self, jdata):
        ''' put new data to calculate diff

            The raw input data format:
            [{
                "LockIndex": 0,
                "Key": "cm/values/1.0/components/AllPhone/cluster/IPVersionPreference",
                "Flags": 0,
                "Value": "eyJWYWx1ZSI6IklQdjQifQ==",
                "CreateIndex": 552,
                "ModifyIndex": 552
            }, ...]
        '''
        # 0) input sanity check
        if not self.__data_sanity_check(jdata):
            Debug.error("Error: set_new_data() sanity_check failed")
            return False
        Debug.debug("set_new_data data members: %d" % len(jdata))

        # 1) find differ instance
        differ = self.__get_differ_instance(jdata)
        if not differ:
            return True

        # 2) calculate_diff
        Debug.notice("%s calculate diff ..." % differ.inst_name);
        diff_data = differ.make_diff(jdata)

        return True

