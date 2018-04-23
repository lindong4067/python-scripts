#!/usr/bin/env python
# --coding:utf-8--


import sys, os
import re
from debug import Debug
from utils import *


class Service(object):
    ''' consul service interface '''

    # Align to consul health check result code:
    # 0     - passing
    # 1     - warning
    # other - critical
    SERVICE_PASSING = 0
    SERVICE_WARNING = 1
    SERVICE_CRITICAL = 2

    ''' Consul service '''

    def service_register(self, service_name, service_ip, service_port,
                         tags=[], script=[], interval="10s", status=""):
        ''' '''

        # make basic service
        service_id = "%s@%s:%d" % (service_name, service_ip, service_port)
        service = {
            "ID": service_id,
            "Name": service_name,
            "Tags": tags,
            "Address": service_ip,
            "Port": service_port,
            "EnableTagOverride": False,
        }

        # make service "Check"
        if script:
            checks = {}
            if type(script) == type(""):
                script = [script]
            checks["Args"] = script
            checks["Interval"] = interval
            if interval in ("passing", "warning", "critical"):
                checks["Status"] = status

            service["Check"] = checks

        # register service to consul
        http_put_request(get_consul_address(),
                         "/v1/agent/service/register",
                         service)

    def service_deregister(service_name, service_ip, service_port):
        ''' '''
        pass


class FdsService(Service):
    def __init__(self, script_file=""):
        super(Service, self).__init__()
        self._service_name = "oam_fds-fdsserver"
        self._script_file = script_file
        self._components = self._get_components()
        self._product_verson = self._get_product_verson()

    def _get_product_verson(self):
        '''
        return True if state is ready
        '''
        config_file = "/opt-mpc/FDS/www/tool/config/config.xml"
        if not os.path.exists(config_file):
            return ""
        cmd = '''grep VERSIONNUMBER /opt-mpc/FDS/www/tool/config/config.xml | \
                 sed -e 's/<VERSIONNUMBER>//;s/<\/VERSIONNUMBER>//;s/\s//g'
              '''
        data = os.popen(cmd).read()
        if not data:
            return ""
        return data.strip()

    def _fdsserver_is_ready(self):
        '''
        check fdsserver is ready
        return True if state is ready
        '''
        cmd = "netstat -napt 2>&1 | grep 10000 | grep FDSServer"
        data = os.popen(cmd).read()
        if not data:
            Debug.error("query fdsserver state error, command: %s!" % cmd)
            return False
        Debug.debug("FDSServer: %s" % data)
        return True

    def _get_components(self):
        ''' query components, the result like:
            {
                "Statistics":   "ACTIVE", 
                "Billing":      "ACTIVE", 
                "LocationDataStream":   "ACTIVE", 
                ...
            }
        '''
        cmd = r'fdsinstall  -u Setup -p Earth_#10 -s'
        data = os.popen(cmd).read()
        if not data:
            Debug.error("query components state error: %s" % cmd)
            return None

        # parse state
        lines = data.split('\n')
        components = {}
        for line in lines:
            # FSC-Event/4.1/linux-eagle-32/1    ACTIVE      linux-eagle-32
            pattern = r'([^/]*)\/(\d\.\d)\/([^/]*)\/(\d)\s*(\w+)\s+'
            matchObj = re.match(pattern, line)
            if matchObj:
                components[matchObj.group(1)] = matchObj.group(5)
                # components[matchObj.group(1)] = {
                #    "Version": matchObj.group(2),
                #    "State": matchObj.group(5)
                # }

        return components

    def register_fdsserver(self, fds_ready=False):
        ''' register fds service to consul.
            The service contain tag likes below, which be encoded 
            into string before put into "Tags:
            {
                "version":      "GMPC17", 
                "fds-server":   {
                        "fds":  "critical", 
                        "components":   {
                                "Statistics":   "ACTIVE", 
                                "Billing":      "ACTIVE", 
                                "LocationDataStream":   "ACTIVE", 
                                ...
                        }
                }
            }
        '''
        fds_status = "passing"
        if not fds_ready:
            fds_status = "critical"

        # service basic info
        service_name = self._service_name
        service_ip, _ = get_consul_address()
        service_port = 10000
        service_check_interval = "15s"
        service_check_script = self._script_file

        # prepare service tags
        fdstag = {
            "version": self._product_verson,
            service_name: {
                "fds": fds_status,
                "components": self._components
            }
        }
        service_tags = [json_dumps(fdstag)]

        # register service to consul
        return self.service_register(
            service_name,
            service_ip,
            service_port,
            service_tags,
            service_check_script,
            service_check_interval,
            fds_status
        )

    def _components_is_ready(self):
        '''
        check all components in ACTIVE
        return True/False
        '''
        # query components
        components = self._components;

        # check all components are in ACTIVE
        for comp_name, comp_stat in components.items():
            if not comp_stat or comp_stat != "ACTIVE":
                Debug.error("Component %s is not in ACTIVE" % comp_name)
                return False

        return True

    def _calculate_service_state(self, fds_ready):
        ''' '''
        # fdsserver is not ready
        if not fds_ready:
            return Service.SERVICE_CRITICAL;

        # fdsserver is ready, but some components is not ready
        components_ready = self._components_is_ready()
        if not components_ready:
            return Service.SERVICE_WARNING;

        # both fdsserver and all components are ready
        return Service.SERVICE_PASSING;

    def service_health_check(self):
        ''' service health check
            returns:
                0   - both fdsserver and all components are ready
                1   - fdsserver is ready, but some components is not ready
                2   - fdsserver is not ready
        '''
        # get fdsserver state
        fds_ready = self._fdsserver_is_ready()

        # update service info
        self.register_fdsserver(fds_ready)

        # check fdsserver and components state
        return self._calculate_service_state(fds_ready)

    def service_is_registered(self):
        consul_ipport = get_consul_address();
        reqfile = "/v1/catalog/service/" + self._service_name
        Debug.debug("service_check service: {0}".format(self._service_name))
        jdata = http_get_request(consul_ipport, reqfile)

        ''' http response shall like:
        [{
            ...
            "ServiceID": "xxx",
            "ServiceName": "{component}",
            "ServiceTags": ["hostname"],
            "ServiceAddress": "{ip}",
            "ServicePort": {port},
            ...
         }, ...]
         '''
        if not type(jdata) is type([]):
            Debug.error("Bad data type(requied []): %s" % str(type(jdata)))
            return False;
        if len(jdata) <= 0 or not "ServiceName" in jdata[0].keys():
            return False
        return True
