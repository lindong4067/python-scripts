#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import json
import xml.etree.cElementTree as ET


def getOneNodeValue(theNode):
    aValue = ''
    i = 0
    while i < len(theNode):
        aChildNode = theNode[i].getchildren()
        '''<fn> tag is dita comments not need'''
        if theNode[i].tag == 'fn':
            continue;
        aParentText = ''
        if theNode[i].text is not None:
            aParentText = (theNode[i].text).strip()

        if aChildNode != []:
            v = 0
            str = ''
            while v < len(aChildNode):
                if aChildNode[v].tag != 'fn' and aChildNode[v].text is not None:
                    if aChildNode[v].tail is not None:
                        str = str + ' ' + (aChildNode[v].text).strip() + (aChildNode[v].tail).strip()
                    else:
                        str = str + ' ' + (aChildNode[v].text).strip()
                v = v + 1

            aValue = aValue + aParentText + str
        else:
            aValue = aValue + aParentText

        i = i + 1

    return aValue.strip().replace('\n', '')


def getGroupName(theRow):
    aGroupName = ''
    if len(theRow) == 2:
        tmpValue = getOneNodeValue(theRow[1])
        stripValue = tmpValue.find(': ')
        if stripValue != -1:
            aGroupName = tmpValue[stripValue + 2:]

    return aGroupName


def getIndex(theListEntry):
    # get each attribute index in dita file
    indexOfParameter = -1
    indexOfDisplayName = -1
    indexOfDescription = -1
    indexOfValue = -1

    if len(theListEntry) != 6 and len(theListEntry) != 5:  # parameter dita must have 6 row in PL 5 row in UG
        return (False, indexOfParameter, indexOfDisplayName, indexOfDescription, indexOfValue)

    indexOfEntry = 0
    for entry in theListEntry:
        oneNodeValue = getOneNodeValue(entry.getchildren())
        if oneNodeValue == "Parameter Namein XML":
            indexOfParameter = indexOfEntry
        elif oneNodeValue == "Parameter Namein GUI":
            indexOfDisplayName = indexOfEntry
        elif oneNodeValue == "Description":
            indexOfDescription = indexOfEntry
        elif oneNodeValue == "Value":
            indexOfValue = indexOfEntry
        indexOfEntry = indexOfEntry + 1

    if indexOfParameter == -1 or indexOfDisplayName == -1 or indexOfDescription == -1 or indexOfValue == -1:
        return (False, indexOfParameter, indexOfDisplayName, indexOfDescription, indexOfValue)
    else:
        return (True, indexOfParameter, indexOfDisplayName, indexOfDescription, indexOfValue)


def getOneParameter(listEntry, theIndex, theGroupName, theDITADict, theComponents, theComponentName):
    parameter = {}
    componentName = theComponentName
    parameter['group'] = theGroupName
    # --------------------------get Parameter Name-------------------------------
    listParameterName = (listEntry[theIndex[1]].getchildren())
    parameterName = getOneNodeValue(listParameterName)

    if parameterName.find(':') != -1:
        componentName = parameterName.split(':')[0]
        parameterName = parameterName.split(':')[1]

    if componentName != 'System Settings' and (componentName in theComponents) == False:
        return

    if len(parameterName) == 0:
        print "component:%s parameter name:%s is Null" % (componentName, listParameterName)
        # raise Exception("component:%s parameter name:%s is Null" %(componentName,listParameterName))

    # -----------------------------get Display name----------------------------
    parameter['display_name'] = getOneNodeValue(listEntry[theIndex[2]].getchildren())
    if len(parameter['display_name']) == 0:
        print "component:%s parameter:%s display name is Null" % (componentName, parameterName)
        # raise Exception("component:%s parameter:%s display name is Null" %(componentName, parameterName))

    # ----------------------------get brief description--------------------------
    briefDescription = getOneNodeValue(listEntry[theIndex[3]].getchildren())
    firstDot = briefDescription.find('.')
    if firstDot == -1:
        parameter['brief_description'] = briefDescription
    else:
        parameter['brief_description'] = briefDescription[0:firstDot]

    if len(parameter['brief_description']) == 0:
        print "component:%s parameter:%s brief_description is Null" % (componentName, parameterName)
        # raise Exception("component:%s parameter:%s display name is Null" %(componentName, parameterName))

    # ------------------------------------get unit-------------------------------------
    i = 0
    listUnit = listEntry[theIndex[4]].getchildren()
    while i < len(listUnit):
        stringText = listUnit[i].text
        if stringText != None:
            stringText = stringText.strip()
        else:
            i = i + 1
            continue
        if stringText[:4] == 'Unit':
            Unit = stringText[5:].strip()
            parameter['unit'] = Unit
            break
        i = i + 1

    parameterMap = {}
    componentDict = {}

    parameterMap[parameterName] = parameter
    componentDict = theDITADict.get(componentName)
    if componentDict == None:
        theDITADict[componentName] = parameterMap
    else:
        # theDITADict.get(componentName).update(oneParameter)
        componentDict.update(parameterMap)


def parseDITA(theRootNode, theDITADict, theComponents, theComponentName=''):
    componentDict = {}
    indexOfHead = 0

    tbody = theRootNode.findall(".//tbody")
    for item in theRootNode.findall(".//thead"):
        tagRow = item.findall("row")
        groupName = getGroupName(tagRow)
        for row in tagRow:
            listEntry = row.getchildren()

            index = getIndex(listEntry)
            if index[0] == False:
                continue

            listRowBody = tbody[indexOfHead].getchildren()
            for row in listRowBody:
                listEntry = row.getchildren()
                if len(listEntry) != 6 and len(listEntry) != 5:  # parameter dita must have 6 row in PL 5 row in UG
                    continue
                getOneParameter(listEntry, index, groupName, theDITADict, theComponents, theComponentName)

        indexOfHead = indexOfHead + 1


def getFromDITA(thePath, theComponents):
    ditaDict = {}
    for fpathe, dirs, fs in os.walk(thePath):
        for file in fs:
            if file.endswith('.dita') == False:
                continue

            DITAFile = os.path.join(fpathe, file)
            root = ET.parse(DITAFile).getroot()

            componentName = root.find('title').text
            componentName = componentName.replace('\n', ' ')
            if componentName == 'System Settings' or componentName in theComponents:
                # for parameter in one component dita file
                parseDITA(root, ditaDict, theComponents, componentName)
            else:
                # for parameter not in one component dita file
                parseDITA(root, ditaDict, theComponents)

    return ditaDict


if __name__ == "__main__":
    GMPCcomponents = (
    'Wireline', 'RequestMonitor', 'Statistics', 'TriggerLocation', 'PPE112', 'ppgps', 'RANEventLocation',
    'PacketLocationFeeder', 'dgpscontroller', 'UPEngine', 'ESABridge', 'GnssAssistanceDataHandler', 'OM', 'lanmonitor',
    'EBMServer', 'Diameter', 'SOAPServer', 'ss7manager', 'IMSRDF', 'Map', 'HTTPServer', 'LocationDataStream',
    'ttmonitor', 'PPRouter', 'AnyPhone', 'AllPhone', 'NetworkStorage', 'Authority', 'PPATI', 'AssistanceDataHandler',
    'Billing', 'CWSL', 'MLP')

    outfile = open('new.json', 'wb')
    json.dump(getFromDITA('../data', GMPCcomponents), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    outfile.close()
