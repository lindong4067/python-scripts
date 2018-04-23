#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import json
import base64
import collections
import commands
import xml.etree.ElementTree as xmlET
import getFromDita

MPSComponents = ()

'''for this hard code components
if any components update will change this'''
GMPCComponents = ('Wireline', 'RequestMonitor', 'Statistics', 'TriggerLocation', 'PPE112', 'ppgps', 'RANEventLocation',
                  'PacketLocationFeeder', 'dgpscontroller', 'UPEngine', 'ESABridge', 'GnssAssistanceDataHandler', 'OM',
                  'lanmonitor', 'EBMServer', 'Diameter', 'SOAPServer', 'ss7manager', 'IMSRDF', 'Map', 'HTTPServer',
                  'LocationDataStream', 'ttmonitor', 'PPRouter', 'AnyPhone', 'AllPhone', 'NetworkStorage', 'Authority',
                  'PPATI', 'AssistanceDataHandler', 'Billing', 'CWSL', 'MLP')

SMPCComponents = (
'AssistanceDataHandler', 'Bssap', 'dgpscontroller', 'ESABridge', 'GnssAssistanceDataHandler', 'lanmonitor', 'OM',
'PositioningRecord', 'ppaecid', 'ppcgi', 'ppesmlc', 'ppgps', 'pplteaecid', 'PPLTEEvent', 'PPRNCEvent', 'ppsas',
'PPSelector', 'PPUTDOA', 'ss7manager', 'Statistics', 'ttmonitor', 'UTDOAOM')

AECIDComponents = ('Aecid', 'ESABridge')


def getAllComponetDir(path):
    global MPSComponents
    componentsDir = {}
    for fpathe, dirs, fs in os.walk(path):
        for dir in dirs:
            if dir in MPSComponents:
                componentsDir[dir] = os.path.join(fpathe, dir)

    return componentsDir


def getOneComponentXMLFiles(path):
    componentFiles = []
    for fpathe, dirs, fs in os.walk(path):
        for file in fs:
            if file == 'Config.xml':
                componentFiles.append(os.path.join(fpathe, file))

    return componentFiles


def getAllComponetXMLFilePath(path):
    componentFileDir = {}
    dirs = getAllComponetDir(path)
    componentFileDir = {}
    for dir in dirs:
        componentFileDir[dir] = getOneComponentXMLFiles(dirs[dir])
    return componentFileDir


def getParameterLevel(nodes):
    parameterLevel = 0;
    for node in nodes:
        parameterAttrib = node.attrib;
        if parameterAttrib.get('Name') == "MONameLevel2":
            parameterLevel = 2;
            break;
        elif parameterAttrib.get('Name') == "MONameLevel3":
            parameterLevel = 3;
            break;
        elif parameterAttrib.get('Name') == "MONameLevel4":
            parameterLevel = 4;
            break;

    return parameterLevel


def covertValueType(theType):
    aType = ''
    if theType == 'StringParameter':
        aType = 'string'
    elif theType == 'IntegerParameter':
        aType = 'integer'
    elif theType == 'DoubleParameter':
        aType = 'double'
    elif theType == 'LongLongParameter':
        aType = 'long'
    return aType


def getXmlData(theFileName, theComponentName, theXmlMap):
    parameterMap = {}
    root = xmlET.parse(theFileName).getroot()
    if root.tag != 'Configuration':
        return

    childrenNode = root.getchildren()
    if len(childrenNode) == 0:
        return

    parameterLevel = getParameterLevel(childrenNode)
    if parameterLevel == 0:
        return

    for child in childrenNode:
        parameterAttrib = child.attrib
        if parameterAttrib.get('Name').find('MONameLevel') != -1:
            continue;

        parameterName = parameterAttrib.get('Name')
        bSystemParameter = (parameterAttrib.get('SystemSetting') == '1')
        if bSystemParameter == True:
            systemParameter = theXmlMap['System Settings'].get(parameterName)
            if systemParameter != None:
                impacts = systemParameter['impacts']
                if theComponentName not in impacts:
                    impacts.append(theComponentName)
                continue

        parameter = collections.OrderedDict()
        parameter['parameter_id'] = parameterAttrib.get('Name')
        parameter['display_name'] = ''
        parameter['level'] = parameterLevel
        parameter['group'] = ''
        parameter['value_type'] = covertValueType(child.tag)
        parameter['default_value'] = child.text.replace('\n\t', '')
        parameter['brief_description'] = ''
        parameter['hide'] = (parameterAttrib.get('Hidden') == '1')
        parameter['runtime_configurable'] = (parameterAttrib.get('RuntimeConfigurable') == '1')
        parameter['config_type'] = parameterAttrib.get('ConfigurationType')
        # parameter['system_setting'] = (parameterAttrib.get('SystemSetting') == '1')
        parameter['impacts'] = [theComponentName]
        parameter['access_keys'] = ()
        parameter['unit'] = ''
        rule = parameterAttrib.get('Rule')
        parameter.update(json.loads(base64.b64decode(rule)))

        if bSystemParameter == True:
            theXmlMap['System Settings'][parameterName] = parameter
        else:
            del parameter['impacts']
            parameterMap[parameterName] = parameter

    return parameterMap


def getXMLMap(path):
    componentsXmlMap = collections.OrderedDict()
    componentsXmlMap['System Settings'] = {}
    componentsXMLfiles = getAllComponetXMLFilePath(path)
    for component in componentsXMLfiles:
        componentMap = collections.OrderedDict()
        for file in componentsXMLfiles[component]:
            componentMap.update(getXmlData(file, component, componentsXmlMap))
        componentsXmlMap[component] = componentMap
    return componentsXmlMap


def checkData(theConfigMap, theDITAMap):
    bCheckPass = True
    global MPSComponents

    # check component are the same
    for i in range(len(MPSComponents)):
        component = MPSComponents[i]
    if theConfigMap.get(component) == None:
        print 'component %s not in Config.xml' % (component)
        bCheckPass = False
    ''' Billing all hide
        dgpscontroller and Billing not in dita
    if theDITAMap.get(component) == None:
        print 'component %s not in DITA file' % (component)
        bCheckPass = False
    '''
    if bCheckPass == False:
        return bCheckPass

    # check dita parameter must not hide in Config.xml
    for component in theDITAMap:
        componentParameters = theDITAMap[component]
        for parameter in componentParameters:
            parameterInXML = theConfigMap[component].get(parameter)
            if parameterInXML == None:
                print 'component %s: parameter [%s] not in Config.xml' % (component, parameter)
                bCheckPass = False
                continue
            if parameterInXML['hide'] == True:
                print 'component %s: parameter [%s] in Config.xml is hide' % (component, parameter)
                bCheckPass = False
                continue

                # check Config.xml not hide parameter all in dita
    for component in theConfigMap:
        componentParameters = theDITAMap.get(component)
        if componentParameters != None:
            for parameter in componentParameters:
                if theDITAMap[component].get(parameter) == None:
                    print 'component %s: not hide parameter [%s] not in DITA' % (component, parameter)
                    bCheckPass = False
                continue

    return bCheckPass


def getProductName():
    global MPSComponents
    productName = commands.getoutput("grep PRODUCT_NAME= /var/opt/setup/site.export | awk -F '=' '{print $2}'")

    if productName == 'smpc':
        MPSComponents = SMPCComponents
    elif productName == 'gmpc':
        MPSComponents = GMPCComponents
    elif productName == 'aecid':
        MPSComponents = AECIDComponents
    else:
        raise SystemExit("get product name error plesase check /var/opt/setup/site.export file is correct")


if __name__ == '__main__':

    outJsonFileName = 'schema.json'
    if len(sys.argv) == 1:
        indir = '.'
    elif len(sys.argv) == 2:
        indir = sys.argv[1]
    elif len(sys.argv) == 3:
        indir = sys.argv[1]
        outJsonFileName = sys.argv[2]
    else:
        raise SystemExit(sys.argv[0] + " [indir [outfile]]")

    getProductName()
    ditaDict = getFromDita.getFromDITA(indir, MPSComponents)
    xmlMap = collections.OrderedDict()
    xmlMap = getXMLMap(indir)

    '''
    if checkData(xmlMap,ditaDict) == False:
        print "****************buildConsulJson error**********"
        raise SystemExit("there some error in DITA file please correct it follow above error message!!!")
    '''

    for component in ditaDict:
        componentParameters = ditaDict[component]
        for parameter in componentParameters:
            # parameterName = componentParameters[parameter]['parameter_id']
            # del componentParameters[parameter]['parameter_id']
            try:
                xmlMap[component][parameter].update(componentParameters[parameter])
            except KeyError:
                print 'component %s: parameter [%s] not in Config.xml' % (component, parameter)
                continue

    outfile = open(outJsonFileName, 'wb')
    json.dump(xmlMap, outfile, sort_keys=False, indent=4, separators=(',', ': '))
    outfile.close()
    print "buildConsulJson success, you can check %s" % outJsonFileName
