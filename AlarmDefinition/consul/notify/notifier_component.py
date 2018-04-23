import abc
from utils import *
from notifier_base import NotifierBase


class NotifierComponent(NotifierBase):
    def __init__(self, jtbuf):
        ''' init parent '''
        self.inst_name = "components"
        super(NotifierComponent, self).__init__(self.inst_name, jtbuf)

    def __notifiy_components(self, jdata):
        ''' one by one notify to each component
            The return data format:
            [
                {
                "Parameter": "cluster/MLPReceiverPortName",
                "Value": "xxx..."
                }, ...
            ]
        '''
        failed_data = {}

        # foreach component
        for comp_key, comp_val in jdata.items():
            values = []

            # foreach parameter: format the result
            for param_key, param_val in comp_val.items():
                values.append({"Parameter": param_key, "Value": param_val["Value"]})

            # get component ip:port
            ipport = self.get_service_ip_port(get_hostname(), comp_key)
            if not ipport:
                Debug.error("notifier can't get %s's ip:port, local hostname: %s" %
                            (comp_key, get_hostname()))
                continue
            Debug.notice("Send to %s: %s" % (ipport, comp_key))
            if Debug.get_debug(self.inst_name):
                Debug.debug("Send data: %s, component: %s" %
                            (comp_key, json_dumps4(values)))

            # send to component, returned True if success
            send_result = self.put_req_by_http2(ipport, values, '/watch')
            if not send_result:
                failed_data[comp_key] = comp_val

        return failed_data

    def _merge_data(self, jarray):
        ''' merge request in array to components/parameter pairs.
            [ {
                "AllPhone": {                               # Component Name
                    "cluster/MLPReceiverPortName": {        # Parameter Path
                        "ModifyIndex": 556,                 # ModifyIndex
                        "Value": "eyJWYWx1ZSI6Ik1M..."      # Value
                    }, ...
                },
              }, {
                "Billing": {                                # Component Name
                    "server/192.168.1.5/SourceName": {
                        "ModifyIndex": 562,
                        "Value": "eyJWYWx1ZSI6OTk5OX0="
                }, ...
              }, ...
            ]

            The return data format:
            {
                "AllPhone": {                               # Component Name
                    "cluster/MLPReceiverPortName": {        # Parameter Path
                        "ModifyIndex": 556,                 # ModifyIndex
                        "Value": "eyJWYWx1ZSI6Ik1M..."      # Value
                    }, ...
                },
                "Billing": {                                # Component Name
                    "server/192.168.1.5/SourceName": {
                        "ModifyIndex": 562,
                        "Value": "eyJWYWx1ZSI6OTk5OX0="
                }, ...
            }
        '''

        values = {}
        for jdata in jarray:
            # look the first as base
            if 0 == len(values):
                values = jdata
                continue

            # merger: foreach component
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
                    if param_val["ModifyIndex"] > base_val["ModifyIndex"]:
                        values[comp_key][param_key] = param_val;

        return values

    def _send_notify(self, jdata):
        """ Send data to components. """
        return self.__notifiy_components(jdata)
