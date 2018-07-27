#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author: jianyong.j.li@ericsson.com

import os, sys, json
import logging
from xml.dom.minidom import parse
import xml.dom.minidom

logging.basicConfig(level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode='a')
    
def json_dumps4(jdata):
    return json.dumps(jdata, indent=4)

def getElementText(element, tagName):
    objects = element.getElementsByTagName(tagName)
    if not object:
        return ""
    return objects[0].childNodes[0].data
    
def getElementAttr(element, attrName):
    if element.hasAttribute(attrName):
        return element.getAttribute(attrName)
    return ""

def get_oid_mapping(filename):
    global gmpc_oid_map, smpc_oid_map, mcn_oid_map, hw_oid_map
    fname = os.path.basename(filename)
    if fname.startswith("GMPC_"):
        return gmpc_oid_map;
    if fname.startswith("SMPC_"):
        return smpc_oid_map;
    if fname.startswith("MCN_"):
        return mcn_oid_map;
    if fname.startswith("hw_"):
        return hw_oid_map;
    logging.error("%%Error: can't found oid_mapping for %s" % filename)
    return None

def load_definitions_from_file(filename, blraise=False, blverbose=False):
    global resourceID, resource_counter
    json_elements = []
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    elements = collection.getElementsByTagName("esa:alarmSpecification")
    namespace = "esa:"
    elements = collection.getElementsByTagName(namespace + "alarmSpecification")
    if not elements:
        namespace = ""
        elements = collection.getElementsByTagName(namespace + "alarmSpecification")
    if not elements:
        logging.error("can't found definition in %s" % filename) 
 
    oid_mapping = get_oid_mapping(filename)
    for element in elements:
        moduleId          = getElementText(element, "esa:moduleId")
        errorCode         = getElementText(element, "esa:errorCode")
        activeDescription = getElementText(element, "esa:activeDescription")

        resourceID = oid_mapping.get("%s:%s" % (moduleId, errorCode))
        if not resourceID and blverbose:
            logging.warning("can't found resourceID for %s: %s:%s" % (
                          filename, moduleId, errorCode))
        
        json_elements.append({
            "active"            : blraise,
            "moduleId"          : moduleId,
            "errorCode"         : errorCode,
            "activeDescription" : activeDescription,
            "resourceID"        : oid_mapping.get("%s:%s" % (moduleId, errorCode))
        })
        
    return json_elements

def raise_clear_alarms(blraise, json_data, blverbose):
    alarm_counter = 0
    for fname, alarms in json_data.items():
        #print("%s alarm base on: %s" % ("Raise" if blraise else "Clear", fname))
        for alarm in alarms:
            moduleId          = alarm.get("moduleId")
            errorCode         = alarm.get("errorCode")
            activeDescription = alarm.get("activeDescription")
            resourceID        = alarm.get("resourceID")
            activeState       = alarm.get("active")

            # skip if not checked
            if not activeState:
                continue
            
            ipaddr = ""
            action = "-r" if blraise else "-c"
            cmd = "fmsendmessage %s %s %s '%s' '%s' %s" % (
                  action, moduleId, errorCode, resourceID, 
                  activeDescription, ipaddr)
            data = ""
            data = os.popen(cmd).read()
            alarm_counter += 1
            print("\n===========(%d)" % alarm_counter)
            print("moduleId         : %s" % moduleId)
            print("errorCode        : %s" % errorCode)
            print("activeDescription: %s" % activeDescription)
            print("resourceID       : %s" % resourceID)
            print("action           : %s" % ("Raise" if blraise else "Clear"))
            if blverbose:
                print("command          : %s" % cmd)
            print("response         : %s" % data)
     
def load_alarm_config(filename):
    if not filename:
        print("%%Error: miss config file")
        return None
     
    data = ""
    try:
        with open(filename, 'r') as f:
            data = f.read()
        json_data = json.loads(data)
    except Exception as error:
        logging.error(error)
        return None
    return json_data
        
def generate_alarm_definitions(blraise, path, blverbose = False):
    if not path:
        path = "/opt/ESA/ESA/conf/fmAlarmDefinitions/"
    if not os.path.isdir(path):
        print("%%Error: Bad path: %s" % path)
        return
                               
    json_data = {}
    for file in os.listdir(path):
        if not file.endswith("xml"):
            continue
        #print(file)
        fname = path + "/" + file
        json_data[file] = load_definitions_from_file(fname, blraise, blverbose)
    return json_data    
    
def parse_alarm_mapping(element, oid_mapping):
        errorCode  = getElementText(element, "ID").strip(' \t\r\n')
        resourceID = getElementText(element, "ResourceID").strip(' \t\r\n')
        for element in element.getElementsByTagName("Mapping"):
            Severity = getElementText(element, "Severity").strip('/* \t\r\n');
            if Severity == "1":
                continue
            moduleId = getElementText(element, "Module").strip('/* \t\r\n');
            oid_mapping["%s:%s" % (moduleId, errorCode)] = resourceID
            #print("moduleId: %s, %s, %s" % (moduleId, errorCode, resourceID))
                    
def foreach_Systemfunction(node, oid_mapping):
    elements = node.getElementsByTagName("Systemfunction")
    if not elements:
        parse_alarm_mapping(node, oid_mapping)
        #sys.exit(0)
        return
    for element in elements:
        foreach_Systemfunction(element, oid_mapping)
        
def parse_oid_from_file(filename):
    if not filename:
        print("%%Error: miss /opt-mpc/FSC/requests/FSC-SystemMonitorCreate_XXX.xml")
        return
        
    xmpc_oid_mapping = {}
    json_elements = []
    
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    elements = collection.getElementsByTagName("PluginController")
    foreach_Systemfunction(elements[0], xmpc_oid_mapping)
    return xmpc_oid_mapping

def usage():
    print("Usage: %s [option] [path/filename]" % os.path.basename(sys.argv[0]))
    print("  -c, --clear [config-file]  clear alarm")
    print("  -r, --raise [config-file]  raise alarm")
    print("  -g, --generate             generate config file")
    #print("  -G, --generate-map [file]  generate-mapping")
    return 1
    
    
def app_main(blraise=True):
    blverbose = False
    blgenerate = False
    blparse_oid = False
    path = ""
    if len(sys.argv) <= 1:
        return usage()
    for arg in sys.argv[1:]:
        if arg == "-h" or arg == "--help":
            return usage()
        elif arg == '-c' or arg == '--clear':
            blraise = False
        elif arg == '-r' or arg == '--raise':
            blraise = True
        elif arg == '-g' or arg == '--generate':
            blgenerate = True
        elif arg == '-G' or arg == '-generate-oid':
            blparse_oid = True
        elif arg == '-v' or arg == '--verbose':
            blverbose = True
        elif not arg.startswith('-'):
            path = arg
        else:
            return usage()
    
    if blgenerate:
        json_data = generate_alarm_definitions(blraise, path, blverbose)
        if json_data:
            print(json.dumps(json_data, indent=4))
    elif blparse_oid:
        json_data = parse_oid_from_file(path)
        if json_data:
            print(json.dumps(json_data, indent=4))
    else:
        json_data = load_alarm_config(path)
        if json_data:
            raise_clear_alarms(blraise, json_data, blverbose)

hw_oid_map = {
    # manual added
    "HW:140101": ".1.1.1", # FIXME 
    "HW:140102": ".1.1.1",
    "HW:140103": ".1.1.1",
    "HW:140104": ".1.1.1",
    "HW:140111": ".1.1.1",
    "HW:140201": ".1.1.1",
    "HW:140202": ".1.1.1",
    "HW:140203": ".1.1.1",
    "HW:140204": ".1.1.1",
    "HW:140211": ".1.1.1",
    "HW:140301": ".1.1.1",
    "HW:140302": ".1.1.1",
    "HW:140303": ".1.1.1",
    "HW:140304": ".1.1.1",
    "HW:140401": ".1.1.1",
    "HW:140411": ".1.1.1",
    "HW:140412": ".1.1.1",
    "HW:140501": ".1.1.1",
    "HW:140601": ".1.1.1",
}

mcn_oid_map = {
    # manual added
    "FDSService:623":       ".1.23.1",
    "FDSService:624":       ".1.23.1",
    "UDAService:625":       ".1.23.2",
    "UDAService:626":       ".1.23.2",
    "PostgreService:627":   ".1.23.3",
    "PostgreService:628":   ".1.23.3",
    "PostgreService:629":   ".1.23.3",
    "RedisService:630":     ".1.23.4",
    "RedisService:631":     ".1.23.4",
    "RedisService:632":     ".1.23.4",
    "OAMCenter:640":        ".1.1.2", # FIXME sendDBConnectionAlarm?
    "WebBE:641":            ".1.1.3"  # FIXME ??
}

gmpc_oid_map = {
    # manual added, accessskey 
    "AssistanceDataHandler:71": ".2.1.3.3.1",

    # auto generated
    "TriggerLocation:114": ".1.6.8",
    "Billing:95": ".1.3.1.2.2",
    "Billing:91": ".1.3.1.1.1",
    "UPEngine:197": ".1.11.5.1",
    "Billing:93": ".1.3.1.2.1",
    "MLP:121": ".1.8.1.2",
    "MLP:126": ".1.10.1",
    "RANEventLocation:506": ".1.10.35",
    "UPEngine:296": ".1.18.1",
    "UPEngine:297": ".1.18.2",
    "HTTPServer:198": ".1.11.5.2",
    "RequestMonitor:176": ".1.11.4.4.1.1.1",
    "ppgps:82": ".1.2.1.10",
    "ppgps:83": ".1.2.1.11",
    "UPEngine:348": ".1.16.2",
    "OM:338": ".1.4.5",
    "OM:339": ".1.4.6",
    "OM:89": ".1.2.3.3",
    "RequestMonitor:130": ".1.10.5",
    "RequestMonitor:447": ".1.11.4.3.2.1.3",
    "RequestMonitor:446": ".1.11.4.3.2.1.2",
    "AllPhone:268": ".1.10.29.2",
    "RequestMonitor:335": ".1.10.22",
    "RequestMonitor:334": ".1.10.21",
    "RequestMonitor:361": ".1.11.1.3",
    "RequestMonitor:138": ".1.10.29.1",
    "CWSL:269": ".1.10.29.4",
    "RequestMonitor:141": ".1.11.2.1.2",
    "HTTPServer:124": ".1.8.3",
    "AssistanceDataHandler:373": ".1.1.2.3",
    "TriggerLocation:280": ".1.6.15",
    "TriggerLocation:281": ".1.6.16",
    "MLP:135": ".1.10.12",
    "PPRouter:74": ".1.2.1.2",
    "ss7manager:108": ".1.6.1.5",
    "TriggerLocation:136": ".1.10.13",
    "PPRouter:131": ".1.10.6",
    "RequestMonitor:143": ".1.11.2.2.1",
    "RequestMonitor:140": ".1.11.2.1.1",
    "ppgps:92": ".1.2.1.13",
    "PPRouter:134": ".1.10.11",
    "RequestMonitor:144": ".1.11.2.2.2",
    "RequestMonitor:145": ".1.11.2.2.3",
    "IMSRDF:612": ".1.4.6",
    "RequestMonitor:621": ".1.11.6.1",
    "RequestMonitor:436": ".1.11.3.2.1.1.2",
    "RequestMonitor:437": ".1.11.3.2.1.1.3",
    "RequestMonitor:435": ".1.11.3.2.1.1.1",
    "TriggerLocation:208": ".1.6.12",
    "UPEngine:81": ".1.2.1.9",
    "UPEngine:86": ".1.2.2.2",
    "UPEngine:84": ".1.2.1.12",
    "UPEngine:85": ".1.2.2.1",
    "TriggerLocation:203": ".1.12.5",
    "CWSL:476": ".1.11.4.1.4",
    "IMSRDF:611": ".1.4.5",
    "FDSCore:206": ".1.14.1",
    "CWSL:282": ".1.6.17",
    "ttmonitor:349": ".1.16.3",
    "RequestMonitor:491": ".1.11.4.6.1.1",
    "UPEngine:79": ".1.2.1.8",
    "UPEngine:78": ".1.2.1.7",
    "PPE112:212": ".1.6.4",
    "UPEngine:76": ".1.2.1.5",
    "UPEngine:75": ".1.2.1.4",
    "PPE112:211": ".1.10.8",
    "UPEngine:73": ".1.2.1.1",
    "OM:391": ".1.4.7",
    "OM:392": ".1.4.8",
    "UPEngine:417": ".1.16.4",
    "RequestMonitor:360": ".1.11.1.2",
    "AssistanceDataHandler:283": ".1.1.2.4",
    "LocationDataStream:424": ".1.5.3",
    "AssistanceDataHandler:285": ".1.1.2.6",
    "AssistanceDataHandler:284": ".1.1.2.5",
    "LocationDataStream:421": ".1.6.21",
    "RequestMonitor:651": ".1.10.2",
    "ttmonitor:218": ".1.15.4",
    "Diameter:455": ".1.21.1.3",
    "ttmonitor:215": ".1.15.1",
    "ttmonitor:216": ".1.15.2",
    "ttmonitor:217": ".1.15.3",
    "Diameter:456": ".1.21.1.4",
    "RequestMonitor:473": ".1.11.4.7.1.1",
    "Diameter:459": ".1.21.3",
    "AllPhone:267": ".1.10.18",
    "AllPhone:266": ".1.10.15",
    "Diameter:454": ".1.21.1.2",
    "PacketLocationFeeder:461": ".1.6.21.1",
    "PacketLocationFeeder:462": ".1.6.21.2",
    "Diameter:457": ".1.21.1.5",
    "Diameter:453": ".1.21.1.1.1",
    "MLP:118": ".1.7.2",
    "IMSRDF:366": ".1.10.32",
    "IMSRDF:367": ".1.10.33",
    "IMSRDF:365": ".1.10.31",
    "SOAPServer:332": ".1.10.19",
    "SOAPServer:333": ".1.10.20",
    "IMSRDF:368": ".1.10.34",
    "SOAPServer:331": ".1.8.4",
    "MLP:117": ".1.7.1",
    "OM:385": ".1.19.5",
    "OM:384": ".1.19.4",
    "RequestMonitor:164": ".1.11.3.1.1.1",
    "RequestMonitor:165": ".1.11.3.1.1.2",
    "RequestMonitor:166": ".1.11.3.1.1.3",
    "CWSL:477": ".1.11.4.1.3",
    "AssistanceDataHandler:69": ".1.1.1.1",
    "RequestMonitor:162": ".1.11.4.1.1.1.2",
    "RequestMonitor:163": ".1.11.4.1.1.1.3",
    "OM:412": ".1.22.2",
    "OM:411": ".1.22.1",
    "MLP:199": ".1.12.1",
    "RequestMonitor:168": ".1.11.4.2.1.2",
    "RequestMonitor:169": ".1.11.4.2.1.3",
    "lanmonitor:125": ".1.9.1",
    "UPEngine:370": ".1.2.3.5",
    "TriggerLocation:301": ".1.12.7",
    "ss7manager:205": ".1.6.1.4",
    "PPRouter:357": ".1.10.29",
    "ss7manager:107": ".1.6.1.3",
    "ss7manager:104": ".1.6.1.1.1",
    "PPATI:112": ".1.6.6",
    "ss7manager:109": ".1.6.1.6",
    "UPEngine:415": ".1.2.2.3",
    "RequestMonitor:483": ".1.11.4.4.2.1.3",
    "PPRouter:132": ".1.10.9",
    "MLP:202": ".1.12.4",
    "UPEngine:416": ".1.11.5.3",
    "MLP:96": ".1.3.1.2.3",
    "RequestMonitor:482": ".1.11.4.4.2.1.2",
    "RequestMonitor:174": ".1.11.4.3.1.1.2",
    "RequestMonitor:481": ".1.11.4.4.2.1.1",
    "UPEngine:418": ".1.16.5",
    "RequestMonitor:178": ".1.11.4.4.1.1.3",
    "RequestMonitor:359": ".1.11.1.1",
    "RequestMonitor:173": ".1.11.4.3.1.1.1",
    "RequestMonitor:177": ".1.11.4.4.1.1.2",
    "AssistanceDataHandler:72": ".1.1.2.2",
    "RequestMonitor:175": ".1.11.4.3.1.1.3",
    "AssistanceDataHandler:70": ".1.1.1.2",
    "Map:353": ".1.6.11",
    "OM:382": ".1.19.2",
    "Map:213": ".1.6.5",
    "HTTPServer:347": ".1.16.1",
    "GnssAssistanceDataHandler:402": ".1.20.1.1",
    "UPEngine:329": ".1.6.14",
    "GnssAssistanceDataHandler:405": ".1.20.2.1",
    "GnssAssistanceDataHandler:406": ".1.20.2.2",
    "IMSRDF:356": ".1.10.28",
    "OM:87": ".1.2.3.1",
    "IMSRDF:345": ".1.10.29.6",
    "RequestMonitor:167": ".1.11.4.2.1.1",
    "IMSRDF:355": ".1.10.27",
    "IMSRDF:342": ".1.10.25",
    "OM:621": ".1.11.6.1",
    "OM:381": ".1.19.1",
    "RequestMonitor:445": ".1.11.4.3.2.1.1",
    "Authority:613": ".1.5.4",
    "OM:88": ".1.2.3.2",
    "UPEngine:298": ".1.18.3",
    "Map:115": ".1.6.9",
    "Map:111": ".1.6.3",
    "Map:113": ".1.6.7",
    "RequestMonitor:442": ".1.11.3.2.2.1.3",
    "Statistics:207": ".1.14.3",
    "RequestMonitor:474": ".1.11.4.7.1.2",
    "RequestMonitor:475": ".1.11.4.7.1.3",
    "RequestMonitor:441": ".1.11.3.2.2.1.2",
    "CWSL:300": ".1.12.6",
    "RequestMonitor:440": ".1.11.3.2.2.1.1",
    "RequestMonitor:493": ".1.11.4.6.1.3",
    "OM:204": ".1.13.1",
    "RequestMonitor:492": ".1.11.4.6.1.2",
    "RequestMonitor:210": ".1.10.7",
    "RequestMonitor:354": ".1.10.28",
    "PPATI:133": ".1.10.10",
    "RequestMonitor:352": ".1.6.10",
    "RequestMonitor:351": ".1.3.1.2.5",
    "OM:90": ".1.2.3.4",
    "MLP:265": ".1.10.14",
    "Wireline:336": ".1.10.23",
    "OM:98": ".1.4.1",
    "OM:99": ".1.4.2",
    "PacketLocationFeeder:390": ".1.6.20",
    "IMSRDF:344": ".1.10.26",
    "FDSCore:362": ".1.14.2",
    "RequestMonitor:161": ".1.11.4.1.1.1.1",
    "MLP:306": ".1.10.16",
    "RANEventLocation:501": ".1.21.1.9",
    "RANEventLocation:500": ".1.21.1.8",
    "Map:106": ".1.6.1.2",
    "EBMServer:470": ".1.21.1.6",
    "MLP:147": ".1.8.1.4",
    "MLP:146": ".1.8.1.3",
    "RequestMonitor:465": ".1.11.4.1.2.1.3",
    "RequestMonitor:464": ".1.11.4.1.2.1.2",
    "HTTPServer:120": ".1.8.1.1",
    "MLP:103": ".1.5.2",
    "OM:608": ".1.4.6",
    "OM:609": ".1.4.5",
    "OM:606": ".1.4.6",
    "OM:607": ".1.4.5",
    "OM:604": ".1.4.6",
    "OM:605": ".1.4.5",
    "OM:602": ".1.4.6",
    "OM:603": ".1.4.5",
    "OM:601": ".1.4.5",
    "GnssAssistanceDataHandler:403": ".1.20.1.2",
    "Wireline:337": ".1.10.24",
    "MLP:423": ".1.10.30",
    "EBMServer:471": ".1.21.1.7",
    "RequestMonitor:209": ".1.6.13",
    "OM:101": ".1.4.4",
    "OM:100": ".1.4.3",
    "OM:622": ".1.11.6.2",
    "OM:61": ".1.4.9.1",
    "OM:62": ".1.4.9.2",
    "AnyPhone:307": ".1.10.17",
    "LocationDataStream:422": ".1.6.22",
    "PPRouter:119": ".1.7.3",
    "AnyPhone:304": ".1.6.19",
    "AnyPhone:303": ".1.6.18",
    "RequestMonitor:463": ".1.11.4.1.2.1.1",
    "RequestMonitor:142": ".1.11.2.1.3",
    "PPRouter:110": ".1.6.2",
    "AnyPhone:308": ".1.10.29.3",
    "Wireline:330": ".1.10.29.5",
    "MLP:77": ".1.2.1.6",
    "PPRouter:458": ".1.21.2",
    "RequestMonitor:127": ".1.10.2",
    "OM:615": ".1.4.6",
    "OM:614": ".1.4.5",
    "Authority:201": ".1.12.3",
    "OM:610": ".1.4.6",
    "OM:341": ".1.4.6",
    "OM:340": ".1.4.5"
}

smpc_oid_map = {
    # manual added
    "Aecid:216": ".1.2.2",
    "Aecid:100": ".1.1.1",
    "Aecid:101": ".1.1.2",
    "Aecid:102": ".1.1.3",
    "Aecid:215": ".1.2.1",
    
    # manual added
    "ppesmlc:2004": ".1.20.1.1",
    "ppesmlc:2005": ".1.20.1.2",
    "ppesmlc:1242": ".2.17.1",
    "ppesmlc:1243": ".2.17.2",
    
    # manual added, accessskey 
    "AssistanceDataHandler:49": ".2.1.3.3.1",
    
    # auto generated
    "ss7manager:223": ".2.4.6",
    "PPUTDOA:1404": ".2.1.4.3.2",
    "ss7manager:221": ".2.4.9",
    "PPUTDOA:1403": ".2.1.4.3.1",
    "OM:1231": ".2.15.18",
    "ss7manager:64": ".2.4.3",
    "ss7manager:63": ".2.4.5",
    "ss7manager:62": ".2.4.4",
    "ss7manager:60": ".2.4.2.1",
    "OM:1232": ".2.15.19",
    "OM:1206": ".2.15.11",
    "OM:1213": ".2.14.1",
    "PPSelector:90": ".2.5.5.3.1.1.3",
    "OM:1211": ".2.2.10",
    "OM:1210": ".2.2.9",
    "OM:1216": ".2.14.4",
    "OM:1196": ".2.15.1",
    "OM:1197": ".2.15.2",
    "OM:1198": ".2.15.3",
    "OM:1199": ".2.15.4",
    "ppesmlc:211": ".2.2.18",
    "Statistics:97": ".2.8.1",
    "OM:1207": ".2.15.12",
    "AssistanceDataHandler:114": ".2.1.3.3.4",
    "PPSelector:841": ".2.5.5.7.1.3",
    "PPSelector:840": ".2.5.5.7.1.2",
    "OM:1200": ".2.15.5",
    "ttmonitor:119": ".2.9.4",
    "HTTPServer:65": ".2.5.1.1",
    "ppesmlc:227": ".2.1.1.5",
    "ttmonitor:116": ".2.9.1",
    "UTDOAOM:169": ".2.11.3",
    "OM:1203": ".2.15.8",
    "OM:1204": ".2.15.9",
    "PPSelector:162": ".2.5.5.5.1.1.2",
    "AssistanceDataHandler:501": ".2.1.3.3.3",
    "PPSelector:82": ".2.5.4.1.1.1",
    "PPSelector:83": ".2.5.4.1.1.2",
    "OM:1202": ".2.15.7",
    "PPSelector:163": ".2.5.5.5.1.1.3",
    "PPSelector:86": ".2.5.5.2.1.2",
    "PPSelector:87": ".2.5.5.2.1.3",
    "PPSelector:84": ".2.5.4.1.1.3",
    "PPSelector:85": ".2.5.5.2.1.1",
    "OM:1208": ".2.2.7",
    "OM:1209": ".2.2.8",
    "PPSelector:88": ".2.5.5.3.1.1.1",
    "ppgps:170": ".2.1.3.1.3",
    "PPSelector:838": ".2.5.5.6.1.3",
    "PPSelector:839": ".2.5.5.7.1.1",
    "PPSelector:832": ".2.5.5.4.2.1.3",
    "PPSelector:833": ".2.5.5.5.2.1.1",
    "PPSelector:830": ".2.5.5.4.2.1.1",
    "Bssap:40": ".2.1.1.1",
    "PPSelector:836": ".2.5.5.6.1.1",
    "PPSelector:837": ".2.5.5.6.1.2",
    "PPSelector:834": ".2.5.5.5.2.1.2",
    "Bssap:44": ".2.1.2.2",
    "PPSelector:89": ".2.5.5.3.1.1.2",
    "ppsas:401": ".2.1.1.2",
    "pplteaecid:444": ".2.1.2.6",
    "OM:1239": ".2.2.22",
    "OM:1238": ".2.2.21",
    "OM:1237": ".2.2.20",
    "OM:155": ".2.12.6",
    "OM:152": ".2.12.1",
    "OM:1230": ".2.15.17",
    "OM:1233": ".2.15.20",
    "lanmonitor:94": ".2.6.1",
    "PPSelector:829": ".2.5.5.3.2.1.3",
    "PPSelector:828": ".2.5.5.3.2.1.2",
    "ppesmlc:1236": ".2.16.7",
    "PPSelector:611": ".2.5.6.1",
    "PPSelector:821": ".2.5.4.2.1.1.1",
    "PPSelector:161": ".2.5.5.5.1.1.1",
    "PPSelector:823": ".2.5.4.2.1.1.3",
    "PPSelector:822": ".2.5.4.2.1.1.2",
    "PPSelector:825": ".2.5.4.2.2.1.2",
    "PPSelector:824": ".2.5.4.2.2.1.1",
    "PPSelector:827": ".2.5.5.3.2.1.1",
    "PPSelector:826": ".2.5.4.2.2.1.3",
    "ppesmlc:201": ".2.1.1.3",
    "ppesmlc:203": ".2.1.3.1.6",
    "PPUTDOA:54": ".2.1.4.1.1",
    "ppesmlc:206": ".2.1.1.4",
    "ss7manager:98": ".2.4.8",
    "PPSelector:1302": ".2.5.5.5.1.1.1",
    "PPSelector:1303": ".2.5.5.5.1.1.2",
    "PPSelector:1304": ".2.5.5.5.1.1.3",
    "PPSelector:1305": ".2.5.5.5.2.1.1",
    "PPSelector:1306": ".2.5.5.5.2.1.2",
    "PPSelector:1307": ".2.5.5.5.2.1.3",
    "OM:1228": ".2.15.15",
    "PPSelector:831": ".2.5.5.4.2.1.2",
    "OM:1215": ".2.14.3",
    "OM:1214": ".2.14.2",
    "OM:1226": ".2.15.13",
    "ppsas:171": ".2.1.3.1.4",
    "OM:1224": ".2.2.11",
    "OM:1225": ".2.2.12",
    "AssistanceDataHandler:120": ".2.1.3.3.5",
    "ppgps:202": ".2.1.3.1.5",
    "AssistanceDataHandler:125": ".2.1.3.3.6",
    "ttmonitor:117": ".2.9.2",
    "PPSelector:835": ".2.5.5.5.2.1.3",
    "ss7manager:200": ".2.4.7",
    "OM:172": ".2.12.2",
    "ppesmlc:212": ".2.2.19",
    "ppsas:1219": ".2.16.2",
    "Emap:441": ".2.1.2.3",
    "ppgps:45": ".2.1.3.1.1",
    "PPSelector:55": ".2.1.4.1.2",
    "PPSelector:663": ".2.5.2.3",
    "PPSelector:662": ".2.5.2.2",
    "PPSelector:661": ".2.5.2.1",
    "OM:173": ".2.12.3",
    "OM:174": ".2.12.4",
    "ppaecid:442": ".2.1.2.4",
    "OM:1253": ".2.15.24",
    "OM:1252": ".2.15.23",
    "OM:1251": ".2.15.22",
    "OM:1250": ".2.15.21",
    "ppsas:56": ".2.12.7",
    "PPRNCEvent:1412": ".2.1.1.6",
    "PPRNCEvent:1413": ".2.1.1.7",
    "PPRNCEvent:1410": ".2.1.1.4",
    "GnssAssistanceDataHandler:403": ".1.20.1.2",
    "GnssAssistanceDataHandler:405": ".1.20.2.1",
    "GnssAssistanceDataHandler:406": ".1.20.2.2",
    "PositioningRecord:1222": ".2.16.5",
    "PPSelector:46": ".2.1.3.1.2",
    "OM:1229": ".2.15.16",
    "PPSelector:42": ".2.1.2.1",
    "PositioningRecord:1220": ".2.16.3",
    "AssistanceDataHandler:47": ".2.1.3.2.1",
    "AssistanceDataHandler:48": ".2.1.3.2.2",
    "PPSelector:71": ".2.5.3.2.2",
    "OM:208": ".2.2.15",
    "OM:209": ".2.2.16",
    "OM:1240": ".2.2.23",
    "OM:204": ".2.2.5",
    "OM:205": ".2.2.6",
    "OM:1201": ".2.15.6",
    "OM:12": ".2.1.4.2",
    "PositioningRecord:1223": ".2.16.6",
    "pplteaecid:56": ".2.12.7",
    "PositioningRecord:1221": ".2.16.4",
    "OM:1227": ".2.15.14",
    "Bssap:310": ".2.4.1",
    "PPSelector:72": ".2.5.3.2.3",
    "OM:110": ".2.2.4",
    "PPSelector:70": ".2.5.3.2.1",
    "OM:95": ".2.7.1",
    "OM:1205": ".2.15.10",
    "ppaecid:56": ".2.12.7",
    "ppsas:443": ".2.1.2.5",
    "PPSelector:1218": ".2.16.1",
    "PPLTEEvent:1308": ".2.1.1.3",
    "AssistanceDataHandler:50": ".2.1.3.3.2",
    "PPLTEEvent:1300": ".2.1.1.1",
    "PPLTEEvent:1301": ".2.1.1.2",
    "ttmonitor:118": ".2.9.3",
    "PPSelector:515": ".2.5.5.4.1.1.3",
    "PPSelector:514": ".2.5.5.4.1.1.2",
    "PPSelector:513": ".2.5.5.4.1.1.1",
    "OM:210": ".2.2.17",
    "GnssAssistanceDataHandler:402": ".1.20.1.1",
    "PPRNCEvent:1411": ".2.1.1.5",
    "PPSelector:68": ".2.5.3.1.2",
    "PPSelector:69": ".2.5.3.1.3",
    "PPSelector:67": ".2.5.3.1.1",
    "OM:101": ".2.2.1",
    "OM:102": ".2.2.2",
    "OM:105": ".2.3.2",
    "OM:104": ".2.3.1",
    "OM:109": ".2.2.3",
    "PPRNCEvent:1309": ".2.1.1.8",
    "OM:611": ".2.5.6.1",
    "OM:154": ".2.12.5",
    "OM:612": ".2.5.6.2"
}
            
if __name__ == '__main__':
    try:
        app_main();
    except KeyboardInterrupt:
        pass
    