#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import socket
import consul
import os

CLUSTER_CONF = '/opt/ESA/ESA/conf/cluster.conf'
# CLUSTER_CONF = 'C:/Temp/config/cluster.conf'


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


def get_consul_addr_list():
    c = consul.Consul()
    mess = c.agent.members()
    ips = []
    for m in mess:
        ips.append(m['Addr'])
    return ips


def file_exist(file_name):
    exist = os.path.isfile(file_name)
    return exist


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
