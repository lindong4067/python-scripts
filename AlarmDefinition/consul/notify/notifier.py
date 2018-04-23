#!/usr/bin/env python
# --coding:utf-8--

import threading

from notifier_component import NotifierComponent
from notifier_datastorages import NotifierDatastorages
from notifier_system import NotifierSystem
from utils import *

''' debug purpose '''
module_name = "notifier"
Debug.init_debug(module_name)


class Notifier(threading.Thread):
    ''' Notifier '''

    def __init__(self, jtbuf):
        # init thread
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.inst_name = "notifier"
        self.jtbuf = jtbuf

        # create & initialize notifier instance
        notifier_component = NotifierComponent(jtbuf)
        notifier_datastorage = NotifierDatastorages(jtbuf)
        notifier_system = None  # aecid has no System
        if get_productname() != "aecid":
            notifier_system = NotifierSystem(jtbuf)
        self.notifier_list = {
            "components": notifier_component,
            "system": notifier_system,
            "datastorages": notifier_datastorage
        }
        Debug.notice("notifier_list: %s" % str(self.notifier_list))

    def __merge_data(self, jarray):
        ''' The input data fortmat from jitter buffer:
            [{
                "Type": "{components | system | datastorages}",
                "Value": {
                    "AnyName": AnyValue,
                    ...
                }
              }, ...
            ]

            Grouped by instance name. The output data fortmat:
            {
                {components | system | datastorages}": [
                    {
                    "AnyName": AnyValue,
                    ...
                    }, ...
                ]
            ]
        '''
        values = {};
        for jdata in jarray:
            # FIXME: add basic check

            inst_name = jdata["Type"]
            diff_data = jdata["Value"]
            if (inst_name in values.keys()):
                values[inst_name].append(diff_data);
            else:
                values[inst_name] = [diff_data]
        return values

    def __notifiy_instances(self, jdata):
        ''' Notify each instance by name.
            The input data fortmat:
            {
                "{components | system | datastorages}": {[
                    {
                    "AnyName": AnyValue,
                    ...
                    }, ...
                ]
            ]
        '''
        for inst_key, inst_val in jdata.items():
            # ignore for unknown notifier
            if not inst_key in self.notifier_list.keys():
                Debug.error("Unknown notifier: %s" % inst_key)
                continue;

            # notify the diff to instance
            notifier = self.notifier_list[inst_key]
            if not notifier:
                Debug.error("Undefined notifier: %s" % inst_key)
                continue;

            Debug.notice("notifiy to %s..." % notifier.inst_name);
            notifier.notify(inst_val)

    def __notify_main(self):
        ''' the main loop of notifier thread.
            The input data fortmat from jitter buffer:
            [ {
                "{components | system | datastorages}": [
                    {
                        "AnyName": AnyValue,
                        ...
                    }, ...
                ]
              }, ...
            ]
        '''
        # 2) try to pop data from jitter buffer
        jdata = self.jtbuf.pop_all()
        if len(jdata) <= 0:
            return;
        if Debug.get_debug(module_name):
            Debug.debug("%s" % json_dumps4(jdata))

        # 3) merge multi-diff into a dict.
        Debug.notice("merge poped data ...");
        jdata = self.__merge_data(jdata);
        if Debug.get_debug(module_name):
            Debug.debug("merged data: %s" % json_dumps4(jdata))

        # 4) notifiy to each instance
        self.__notifiy_instances(jdata);

    def run(self):
        ''' override the threading.run '''
        begin_time = 0.0;
        while True:
            # 1) sleep a while
            if (time.time() - begin_time) <= 1.0:
                time.sleep(0.2);
                continue
            begin_time = time.time();

            # 2) run notify
            try:
                self.__notify_main();
            except:
                Debug.fatal("Notifier failed: %s" % str(sys.exc_info()))
