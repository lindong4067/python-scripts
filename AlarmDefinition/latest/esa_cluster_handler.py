#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import socket
import os
import sys
import json
import urllib2
import base64

CLUSTER_CONF = '/opt/ESA/ESA/conf/cluster.conf'
CHECK_FILE = '/opt-mpc/Config/template/config'
EXPORT_FILE = '/var/opt/setup/site.export'
IP_CONFIG = '/opt/local/ip-config.properties'
ALARM_DEFINITION_PATH_HW = '/opt/ESA/ESA/conf/fmAlarmDefinitions/hw_alarmdef.xml'
ALARM_DEFINITION_PATH_GMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_SMPC = '/opt/ESA/ESA/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml'
ALARM_DEFINITION_PATH_AECID = '/opt/ESA/ESA/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml'


def get_local_addr():
    my_name = socket.getfqdn(socket.gethostname())
    my_addr = socket.gethostbyname(my_name)
    return my_addr


def read_file(file_path):
    rf = open(file_path, 'r')
    file_content = rf.read()
    rf.close()
    return file_content


def save_to_file(file_name, str_xml):
    fw = open(file_name, 'w')
    fw.write(str_xml)
    fw.close()
    return


def replace_str_host(str_tar, str_all):
    af = re.sub(u"hostname=\"\d+.\d+.\d+.\d+\"", str_tar, str_all)
    return af


def str_format_host(str_i):
    bf = str.format("hostname=\"{}\"", str_i)
    return bf


def str_format_node_fm(str_n):
    nod = str.format("\"akka.tcp://FMCluster@{}:2551\",", str_n)
    return nod


def str_format_node_ma(str_n):
    nod = str.format("\"akka.tcp://MACluster@{}:2552\",", str_n)
    return nod


def find_spec_str(fm_ma, str_all):
    stss = re.findall("seed-[\s|\S]*?]", str_all)
    for st in stss:
        if fm_ma in st:
            return st


def get_watch_data():
    data = sys.stdin.read()
    data = json.loads(data)
    return data


def get_consul_addr_list():
    _res = get_watch_data()
    if _res:
        ips = []
        for m in _res:
            ips.append(m['Address'])
        return ips


def file_exist(file_name):
    exist = os.path.isfile(file_name)
    return exist


def get_machine_type():
    if os.path.isfile(CHECK_FILE):
        file_c = read_file(CHECK_FILE)
        if 'PRODUCT_NAME=gmpc' in file_c:
            return 'gmpc'
        elif 'PRODUCT_NAME=aecid' in file_c:
            return 'aecid'
        elif 'PRODUCT_NAME=smpc' in file_c:
            return 'smpc'


def get_cluster_name():
    if os.path.isfile(EXPORT_FILE):
        file_e = read_file(EXPORT_FILE)
        if file_e.find('CLUSTER_NAME') >= 0:
            lines = file_e.split('\n')
            for li in lines:
                if li.strip().startswith('CLUSTER_NAME') and li.strip().contains('='):
                    ls = li.strip().split('=')
                    if len(ls) == 2:
                        return ls[1].strip()


def get_version():
    if os.path.isfile(EXPORT_FILE):
        file_e = read_file(EXPORT_FILE)
        if file_e.find('VERSION') >= 0:
            lines = file_e.split('\n')
            for li in lines:
                if li.strip().startswith('VERSION') and li.strip().contains('='):
                    ls = li.strip().split('=')
                    if len(ls) == 2:
                        return ls[1].strip()


def get_consul_key_s(_version, _node, _cluster_name):
    if _version is not None and _node is not None and _cluster_name is not None:
        key = '/v1/kv/cm/values/%s‐%s‐%s/datastorages/esaconfig/%s'.format(_version, _node, _cluster_name, _node)
        key_hw = '/v1/kv/cm/values/%s‐%s‐%s/datastorages/esaconfig/hw'.format(_version, _node, _cluster_name)
        return key, key_hw


def get_file_path(_key):
    file_path = None
    if 'gmpc' in _key:
        file_path = ALARM_DEFINITION_PATH_GMPC
    elif 'smpc' in _key:
        file_path = ALARM_DEFINITION_PATH_SMPC
    elif 'aecid' in _key:
        file_path = ALARM_DEFINITION_PATH_AECID
    elif 'hw' in _key:
        file_path = ALARM_DEFINITION_PATH_HW
    return file_path


def get_consul_value(_ip, port, key):
    request = urllib2.Request('http://%s:%s/v1/kv/%s' % (_ip, port, key))
    response = urllib2.urlopen(request)
    res = response.read()
    _res = json.loads(res)
    if _res:
        _res_value = base64.b64decode(_res[0]['Value'])
        return _res_value


class Properties:
    def __init__(self, file_name):
        self.file_name = file_name
        self.properties = {}
        try:
            f = open(self.file_name, 'r')
            for line in f:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        except Exception, e:
            raise e.message
        else:
            f.close()

    def get_value(self, key):
        if key in self.properties:
            return self.properties[key]


def get_consul_ip_port(config_path):
    props = Properties(config_path)
    _ip = props.get_value('consulAddress')
    _port = props.get_value('consulPort')
    return _ip, _port


def sync_definition():
    ip_port = get_consul_ip_port(IP_CONFIG)
    _node = get_machine_type()
    _version = get_version()
    _cluster_name = get_cluster_name()
    keys = get_consul_key_s(_version, _node, _cluster_name)
    if keys is not None:
        for key in keys:
            value = get_consul_value(ip_port[0], ip_port[1], key)
            file_path = get_file_path(key)
            save_to_file(file_path, value)


if __name__ == '__main__':
    if file_exist(CLUSTER_CONF):
        file_all = read_file(CLUSTER_CONF)
        ip = get_local_addr()
        str_ip = str_format_host(ip)
        file_all = replace_str_host(str_ip, file_all)

        spec_str_fm = find_spec_str('FM', file_all)
        spec_str_ma = find_spec_str('MA', file_all)

        ip_list = get_consul_addr_list()

        seed_nodes_fm = 'seed-nodes=['
        for i in ip_list:
            seed_nodes_fm += str_format_node_fm(i)
        seed_nodes_fm = seed_nodes_fm[:-1] + ']'

        seed_nodes_ma = 'seed-nodes=['
        for i in ip_list:
            seed_nodes_ma += str_format_node_ma(i)
        seed_nodes_ma = seed_nodes_ma[:-1] + ']'

        file_all = file_all.replace(spec_str_fm, seed_nodes_fm)
        file_all = file_all.replace(spec_str_ma, seed_nodes_ma)

        save_to_file(CLUSTER_CONF, file_all)

        sync_definition()
