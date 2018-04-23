#!/usr/bin/env python

import sys, os
import re
from debug import Debug

from utils import *


# Align to consul health check result code:
    # 0     - passing
    # 1     - warning
    # other - critical
SERVICE_PASSING  = 0
SERVICE_WARNING  = 1
SERVICE_CRITICAL = 2

#function :Both of services are the same name ,but they have different serviceid, serviceid includes ip and port.
# So, as for every service, to check the ip and port
    
def get_service_ipport(servicename, serviceid):
    consul_ipport = get_consul_address()
    reqfile = "/v1/catalog/service/" + servicename 
    jdata = http_get_request(consul_ipport, reqfile)
    Debug.debug("query service: %s" % json_dumps4(jdata))
    '''
       {
        "Node": "linux-eagle-42", 
        "Datacenter": "dc2", 
        "CreateIndex": 72590, 
        "ServiceName": "intf-udp_sip", 
        "TaggedAddresses": {
            "wan": "10.180.30.42", 
            "lan": "10.180.30.42"
        }, 
        "ModifyIndex": 72590, 
        "ServicePort": 5060, 
        "ServiceID": "intf-udp_sip@10.180.30.42:5060", 
        "ServiceAddress": "10.180.30.42", 
        "Address": "10.180.30.42", 
        "ServiceTags": [
            "version:GMPC17"
        ], 
        "NodeMeta": {
            "consul-network-segment": ""
        }, 
        "ServiceEnableTagOverride": false, 
        "ID": "460a16cb-f28d-5fdf-40e7-92e960c440f0"
    }, 
  ''' 
    # extract port
    for it in jdata:
        if ("ServiceID" in it.keys() and "ServiceAddress" in it.keys() and "ServicePort" in it.keys()):
               # service_id = it["ServiceID"];
                ipaddr = it["ServiceAddress"];
                port = it["ServicePort"]
                if not ipaddr:
                    # FIXME
                    ipaddr = "127.0.0.1"
                if serviceid == it["ServiceID"]:
                   print("service Id: %s" % serviceid)
                   state =  health_check(ipaddr + ":" + str(port))
                   print("service state: %d" % state)
                   return state




def health_check(ipport):
   ''' health check
       returns:
             0   -port is opened and listening
             2   -port is not opened 
   '''
   cmd = "netstat -napu 2>&1 | grep " + ipport  + " | grep PluginContain"
   data = os.popen(cmd).read()
   if not data:
        Debug.error("query udp sip state error, command: %s!" % cmd)
        return SERVICE_CRITICAL
   Debug.debug("port status: %s" % data)
   return SERVICE_PASSING

if __name__=="__main__":
  # When CONSUL_IP can't get from environ, get it from config file
  # and update to environ 
     if not "CONSUL_IP" in os.environ.keys():
         reqcmd = '''
           cat /var/opt/setup/site.export | egrep '^CONSUL_IP=.*$' | \
           awk -F= '{ print $2 }'
           '''
     resp = os.popen(reqcmd, "r").read()
     if resp:
         resp = resp.strip('"\n')
         os.environ["CONSUL_IP"] = resp
     print("CONSUL_IP: %s" % str(resp))
     status =get_service_ipport(sys.argv[1], sys.argv[2]) 
     sys.exit(status); 


