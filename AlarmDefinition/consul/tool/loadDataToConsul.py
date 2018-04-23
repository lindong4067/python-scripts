#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import getopt
import json
import base64
import time
import commands
import collections

valuePrefixURL = ''
schemaPrefixURL = ''


def getPrefixURL():
    global valuePrefixURL
    global schemaPrefixURL

    productName = commands.getoutput("grep PRODUCT_NAME= /var/opt/setup/site.export | awk -F '=' '{print $2}'")

    if productName == 'smpc':
        schemaPrefixURL = 'cm/schema/18-smpc/'
        valuePrefixURL = 'cm/values/18-smpc-cluster/'
    elif productName == 'gmpc':
        schemaPrefixURL = 'cm/schema/18-gmpc/'
        valuePrefixURL = 'cm/values/18-gmpc-cluster/'
    elif productName == 'aecid':
        schemaPrefixURL = 'cm/schema/18-aecid/'
        valuePrefixURL = 'cm/values/18-aecid-cluster/'
    else:
        raise SystemExit("get product name error plesase check /var/opt/setup/site.export file is correct")


def getSystemKVList(theParameter, theComponent, theSystemSchemaList, theSystemValueList):
    global valuePrefixURL
    global schemaPrefixURL
    schemaKV = {}
    schemaKV['key'] = schemaPrefixURL + 'system/' + theParameter['parameter_id']
    schemaKV['value'] = base64.b64encode(json.dumps(theParameter))
    theSystemSchemaList.append(schemaKV)

    if theParameter['level'] == 2:
        valueKV = {}
        valueKV['key'] = valuePrefixURL + 'system/cluster/' + theParameter['parameter_id']
        valueKV['value'] = base64.b64encode(theParameter['default_value'])
        theSystemValueList.append(valueKV)


def getComponentKVList(theParameter, theComponent, theComponentSchemaList, theComponentValueList):
    # theParameter['impacts'] = []
    global valuePrefixURL
    global schemaPrefixURL
    schemaKV = {}
    schemaKV['key'] = schemaPrefixURL + 'components/' + theComponent + '/' + theParameter['parameter_id']
    schemaKV['value'] = base64.b64encode(json.dumps(theParameter))
    theComponentSchemaList.append(schemaKV)

    if theParameter['level'] == 2:
        valueKV = {}
        valueKV['key'] = valuePrefixURL + 'components/' + theComponent + '/cluster/' + theParameter['parameter_id']
        valueKV['value'] = base64.b64encode(theParameter['default_value'])
        theComponentValueList.append(valueKV)


def getConsulKVList(theMap, theSystemSchemaList, theSystemValueList, theComponentSchemaList, theComponentValueList):
    for component in theMap:
        componentParameters = theMap[component]
        for parameter in componentParameters:
            parameterSchema = componentParameters[parameter]
            if component == 'System Settings':
                getSystemKVList(parameterSchema, component, theSystemSchemaList, theSystemValueList)
            else:
                getComponentKVList(parameterSchema, component, theComponentSchemaList, theComponentValueList)


def consulImport(theDataList):
    tempFileName = 'temp_' + str(time.time())
    tempFile = open(tempFileName, 'wb')
    json.dump(theDataList, tempFile, sort_keys=False, indent=4, separators=(',', ': '))
    tempFile.close()
    # os.system('consul kv import @' + tempFileName + '> /dev/null 2>&1')
    os.system('consul kv import @' + tempFileName)
    os.remove(tempFileName)


def importParameterToConsul(theFile):
    global valuePrefixURL
    global schemaPrefixURL
    with open(theFile, 'r') as f:
        data = json.load(f);
        systemSchemaList = []
        systemValueList = []
        componentSchemaList = []
        componentValueList = []

        getConsulKVList(data, systemSchemaList, systemValueList, componentSchemaList, componentValueList)

        os.system('consul kv delete -recurse ' + schemaPrefixURL + 'components' + '> /dev/null 2>&1')
        os.system('consul kv delete -recurse ' + schemaPrefixURL + 'system' + '> /dev/null 2>&1')
        os.system('consul kv delete -recurse ' + valuePrefixURL + 'components' + '> /dev/null 2>&1')
        os.system('consul kv delete -recurse ' + valuePrefixURL + 'system' + '> /dev/null 2>&1')

    consulImport(systemSchemaList)
    consulImport(systemValueList)
    consulImport(componentSchemaList)
    consulImport(componentValueList)


def loadDatastorage(theFile):
    global valuePrefixURL
    global schemaPrefixURL
    with open(theFile, 'r') as f:
        data = json.load(f);
        datastorageSchemaList = []
        for datastorage in data:
            schemaKV = {}
            schemaKV['key'] = schemaPrefixURL + 'datastorages/' + datastorage
            schemaKV['value'] = base64.b64encode(json.dumps(data[datastorage]))
            datastorageSchemaList.append(schemaKV)

        os.system('consul kv delete -recurse ' + schemaPrefixURL + 'datastorages' + '> /dev/null 2>&1')
        consulImport(datastorageSchemaList)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:d:", ["parameterfile=", "datastoragefile="])
    except getopt.GetoptError:
        print 'Error: loadDataToConsul.py -p parameterfile'
        print 'Error: loadDataToConsul.py -d datastoragefile'
        sys.exit(2)

    getPrefixURL()
    parameterfile = ''
    datastoragefile = ''
    for opt, arg in opts:
        if opt == "-h":
            print 'Error: loadDataToConsul.py -p parameterfile'
            print 'Error: loadDataToConsul.py -d datastoragefile'
        elif opt == '-p':
            parameterfile = arg
            importParameterToConsul(parameterfile)
        elif opt == '-d':
            datastoragefile = arg
            loadDatastorage(datastoragefile)
