import abc
from utils import *
import pdb
from notifier_base import NotifierBase


class NotifierDatastorages(NotifierBase):
    def __init__(self, jtbuf):
        ''' init parent '''
        self.inst_name = "datastorages"
        super(NotifierDatastorages, self).__init__(self.inst_name, jtbuf)

    def notifiy_datastorages(self, jdata):
        ''' one by one notify to each datastorage
            The return data format:
            [ 
                {
                "key": "datastorages[i]/key[i]",
                "Value": "xxx..."
                "Command":"UPDATE/REMOVE/REMOVEALL"
                }, ...
            ]
        '''
        failed_data = {}
        # foreach datastorages
        ## var name modify
        for comp_key, comp_val in jdata.items():
            values = []

            # foreach parameter: format the result
            for param_key, param_val in comp_val.items():
                values.append({"Key": param_key, "Value": param_val["Value"], "Command": param_val["Command"]})

            # get component ip:port
            ipport = self.get_service_ip_port(get_hostname(), comp_key)
            if not ipport:
                Debug.error("notifier can't get %s's ip:port, local hostname: %s" %
                            (comp_key, get_hostname()))
                continue
            Debug.notice("Send to %s: %s" % (ipport, comp_key))
            if Debug.get_debug(self.inst_name):
                Debug.debug("Send data: %s, datastorages: %s" %
                            (comp_key, json_dumps4(values)))

            # send to component, returned True if success
            send_result = self.put_req_by_http2(ipport, values, '/watch')  # hard code
            if not send_result:
                failed_data[comp_key] = comp_val

        return failed_data

    def _merge_data(self, jarray):

        ''' The return data format:
            {
                "datastorages[i]": {                               # datastorages Name
                    "datastorages[i]/key[i]": {        # key value
                        "ModifyIndex": 556,                 # ModifyIndex
                        "Value": "eyJWYWx1ZSI6Ik1M..."      # Value
                        "Command":"UPDATE/REMOVE/REMOVEALL"
                    }, ...
                    }....
            }
        '''

        values = {};

        for jdata in jarray:
            # look the first as base
            if 0 == len(values):
                values = jdata
                continue

            # merger: foreach datastorages
            for comp_key, comp_val in jdata.items():
                # component not exists in values, add it.
                if not comp_key in values.keys():
                    values[comp_key] = comp_val
                    continue

                # merger: foreach parameter
                for param_key, param_val in comp_val.items():
                    # parameter not exists in component, add it.
                    if not param_key in values[comp_key].keys():
                        values[comp_key][param_key] = param_val
                        continue

                    # make base value
                    base_val = values[comp_key][param_key]

                    # new than base_val, update it
                    if (param_val["Command"] == 'REMOVE' or param_val["Command"] == 'REMOVEALL'):
                        values[comp_key][param_key] = param_val;
                    else:
                        if (param_val["ModifyIndex"] > base_val["ModifyIndex"]):
                            values[comp_key][param_key] = param_val;

        return values

    def _send_notify(self, jdata):
        """ xxxx """
        return self.notifiy_datastorages(jdata)
