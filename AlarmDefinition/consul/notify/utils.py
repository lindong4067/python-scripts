#!/usr/bin/env python
# --coding:utf-8--

import os, sys
import json, time
import base64
import socket
import traceback
from debug import Debug

if sys.version_info < (3, 0):
    import httplib as httplib
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    import http.client as httplib
    from http.server import BaseHTTPRequestHandler, HTTPServer


def getint(str, default=0):
    if str and str.isdigit():
        return int(str)
    return default;


def json_parse(data):
    ''' parse json string '''
    try:
        if not data:
            return {}
        return json.loads(data);
    except Exception as err:
        Debug.error("Error: parse data (%.25s...) error: %s" % (data, err))
    return {};


def json_dumps4(jdata):
    ''' dump json string with pretty format '''
    try:
        return json.dumps(jdata, indent=4)
    except Exception as err:
        Debug.error("Error: dump data error: %s" % (err))
    return "";


def json_dumps(jdata):
    ''' dump json string inline '''
    try:
        return json.dumps(jdata)
    except Exception as err:
        Debug.error("Error: dump data error: %s" % (err))
    return "";


def base64decode(data):
    ''' base64 decode string '''
    try:
        val = base64.b64decode(data).decode("UTF-8")
        if val is not None:
            if type(val) == str:
                return val
            return val.decode("UTF-8")
    except Exception as err:
        Debug.error("Error: b64decode data (%.25s...) error: %s" % (data, err))
    return ""


def getenv(key, default=""):
    ''' get the env string value by key '''
    if key in os.environ.keys():
        val = os.environ[key].strip()
        if val != "":
            return val
    return default


def getenv_int(key, default=0):
    ''' get the env integer value by key '''
    val = getenv(key)
    if val and val.isdigit():
        return int(val)
    return default;


''' Common APIs '''


def get_productname():
    return getenv("PRODUCT_NAME", "gmpc")


def get_hostname():
    return socket.gethostname()


def get_consul_schema_version():
    version = "18-{0}".format(get_productname())
    return version


def get_consul_version_node():
    version = "18-{0}-cluster".format(get_productname())
    return version


def get_consul_address():
    ipaddr = getenv("CONSUL_IP", default="127.0.0.1")
    port = getenv_int("CONSUL_REAL_PORT", default=8500)
    return ipaddr, port


def get_filter_httpd_address():
    ipaddr = getenv("NOTIFY_FILTER_IP", default="127.0.0.1")
    port = getenv_int("NOTIFY_FILTER_PORT", default=8000)
    return ipaddr, port


def get_notify_filter_address():
    ipaddr, port = get_filter_httpd_address()
    return ipaddr + ":" + str(port)


def get_notify_data_path():
    data_path = getenv("NOTIFY_FILTER_DATA_PATH", default="/tmp/notify_filter")
    if not os.path.exists(data_path):
        os.system("mkdir -p " + data_path)
    return data_path


def http_get_request(ipport, reqfile):
    ''' request http server, return JSON response '''
    Debug.notice("GET http://{0}{1}".format(
        ':'.join(str(n) for n in ipport), reqfile))
    resp = ""
    try:
        httpClient = httplib.HTTPConnection(*ipport, timeout=100)
        httpClient.request('GET', reqfile)

        response = httpClient.getresponse()
        Debug.notice("HTTP response: %s" % response.status)

        resp = response.read().decode();
    except Exception as err:
        Debug.error("%%Error post_req: %s" % str(err))
    finally:
        if httpClient:
            httpClient.close()
    return json_parse(resp)


def http_put_request(ipport, reqfile, jdata):
    ''' request http server, return JSON response '''
    Debug.debug("PUT http://{0}{1} : {2}".format(
        ':'.join(str(n) for n in ipport), reqfile,
        jdata)
    )
    resp = ""
    try:
        httpClient = httplib.HTTPConnection(*ipport, timeout=100)
        headers = {"Content-type": "application/json"}
        httpClient.request('PUT', reqfile, json_dumps(jdata), headers)

        response = httpClient.getresponse()
        Debug.debug("HTTP response: %s" % response.status)

        resp = response.read().decode();
    except Exception as err:
        Debug.error("%%Error post_req: %s" % str(err))
    finally:
        if httpClient:
            httpClient.close()
    return json_parse(resp)


GMPC_COMPONENTS = (
    "Statistics", "Billing", "LocationDataStream", "HTTPServer",
    "dgpscontroller", "FSC-SystemMonitor", "AssistanceDataHandler",
    "ESABridge", "Map", "FSC-EventLog", "FSC-CGIEventLog", "lanmonitor",
    "FSC-Event", "FSC-LTEEventLog", "PPE112", "PPRouter", "SOAPServer",
    "ttmonitor", "RANEventLocation", "RequestMonitor", "EBMServer",
    "FSC-OMEventLog", "MLP", "CWSL", "Wireline", "AnyPhone", "ppgps",
    "GnssAssistanceDataHandler", "Diameter", "OM", "AllPhone",
    "ss7manager", "PPATI", "FSC-SAIEventLog", "Authority", "IMSRDF",
    "TriggerLocation", "UPEngine", "PacketLocationFeeder",
    "NetworkStorage"
)

SMPC_COMPONENTS = (
    "FSC-Event", "Statistics", "dgpscontroller", "lanmonitor",
    "PPSelector", "ss7manager", "OM", "Bssap", "ppcgi", "ppaecid",
    "pplteaecid", "ppgps", "ttmonitor", "GnssAssistanceDataHandler",
    "PPUTDOA", "UTDOAOM", "ppsas", "ppesmlc", "PositioningRecord",
    "PPLTEEvent", "PPRNCEvent", "AssistanceDataHandler", "FSC-EventLog",
    "FSC-CGIEventLog", "FSC-CELLIDEventLog", "FSC-LTEEventLog",
    "FSC-PDEEventLog", "FSC-PMCEventLog", "FSC-FixedXYEventLog",
    "FSC-OMEventLog", "FSC-SystemMonitor", "ESABridge"
)

if __name__ == '__main__':
    Debug.debug_flags = {"aaa": False, "bbb": False}

    Debug.set_debug('aaa', True)
    Debug.set_debug('ccc', True)
    Debug.error("test", Debug.get_debug('aaa'), Debug.get_debugs())
