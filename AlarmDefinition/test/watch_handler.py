#!/usr/bin/env python
import httplib
import sys, os
import json, base64
import urllib
from imaplib import Debug

from utils import *


class WatchHandler(object):
    def __init__(self):
        pass

    def post_to_notify_filter(self, jdata, reqfile):
        ipaddr, port = get_filter_httpd_address();
        Debug.notice("notify_filter ipport: %s:%u" % (ipaddr, port))

        try:
            httpClient = httplib.HTTPConnection(ipaddr, port, timeout=100)

            headers = {"Content-type": "application/json"}
            httpClient.request('PUT', reqfile, json.dumps(jdata), headers)
            response = httpClient.getresponse()

            # FIXME: log error
            resp = response.read();
            if resp:
                resp = resp.decode()
            if (response.status != 200):
                Debug.error("WatchHandler send to notify_filter failed!")
            Debug.notice("response (status %d): %s" % (response.status, resp))
        except Exception as err:
            Debug.error(err)
        finally:
            if httpClient:
                httpClient.close()

    def run(self):
        # 1) read watch data from stdin
        data = sys.stdin.read()

        # SPECIAL:
        # When delete the last value in /datastorages/ or delete 
        # keys recursely from consul, the values received are 'null\n'.
        # To let message be sent to datastorages, Make a pseudo data.
        #
        if data.startswith('null'):
            data = [{
                "Key": "cm/values/{0}/datastorages/".
                    format(get_consul_version_node()),
                "CreateIndex": 0,
                "ModifyIndex": 0,
                "LockIndex": 0,
                "Flags": 0,
                "Value": None,
                "Session": ""
            }]
            data = json_dumps(data)
        Debug.notice("WatchHandler get data: %.35s ..." % data)

        # 2) parse input data and do sanity check
        #    Send data to notify_filter
        jdata = json_parse(data)
        self.post_to_notify_filter(jdata, "/watch_data")
        Debug.notice("Done")


if __name__ == '__main__':
    try:
        # 1) Init debug & log
        Debug.config(get_notify_data_path() + "/watch.log", True)

        # 2) create WatchHandler
        watch_handler = WatchHandler()
        watch_handler.run()
    except Exception as err:
        Debug.fatal("Error: %s" % (err))
