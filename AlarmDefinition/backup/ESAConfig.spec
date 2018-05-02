#
# spec file for package: ESAConfig
#

%define _topdir @MACS_MIRROR@/rpm_topdir/

Name:      ESAConfig
Summary:   Ericsson Snmp Agent config for MPS
Version:   @RPMVERSION@
Release:   1
License:   (C) Ericsson AB 2010
Vendor:    Ericsson AB
Packager:  Ericsson AB
Group:     Applications/MPS
Source:    dummy_source
BuildRoot: @MACS_MIRROR@/%{name}-build
Prefix:    /opt-mpc
Requires:	esa
Requires:	ssm

%define TARGET_DIR /opt-mpc/ESAConfig

%description


%prep
echo Building %{name}-%{version}-%{release}


%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}
pwd
# copy all scripts, libs, etc
mkdir -p ${RPM_BUILD_ROOT}/%{TARGET_DIR}
cd ${RPM_BUILD_ROOT}/../
mkdir -p ${RPM_BUILD_ROOT}/opt/ESA
ln -s /usr/local/esa ${RPM_BUILD_ROOT}/opt/ESA/ESA
cp -r @MACS_MIRROR@/ESAConfig ${RPM_BUILD_ROOT}/%{prefix}
mkdir -p ${RPM_BUILD_ROOT}/opt/ESA/SSM/config/
ln -s /opt-mpc/ESAConfig/HW/config/hw_monitors.cfg ${RPM_BUILD_ROOT}/opt/ESA/SSM/config/hw_monitors.cfg
mkdir -p ${RPM_BUILD_ROOT}/usr/local/esa/conf/fmAlarmTranslations/
ln -s /opt-mpc/ESAConfig/HW/TrapTranslations/hw_alarmtrans.xml ${RPM_BUILD_ROOT}/usr/local/esa/conf/fmAlarmTranslations/hw_alarmtrans.xml
mkdir -p ${RPM_BUILD_ROOT}/usr/local/esa/conf/fmAlarmDefinitions/
ln -s /opt-mpc/ESAConfig/HW/AlarmDefinitions/hw_alarmdef.xml ${RPM_BUILD_ROOT}/usr/local/esa/conf/fmAlarmDefinitions/hw_alarmdef.xml
mkdir -p ${RPM_BUILD_ROOT}/usr/local/esa/conf/pmCounters/
mkdir -p ${RPM_BUILD_ROOT}/var/ESA/AlarmService/log
cp -fr @MACS_MIRROR@/alarms.log ${RPM_BUILD_ROOT}/var/ESA/AlarmService/log/alarms.log 


%clean
# remove tmp build directory
[ ${RPM_BUILD_ROOT} != "/" ] && rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/infoSystem.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/trapDestCfg.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/communityCfg.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/vacmCfg.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/agent.cfg
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/agent.state
%config %attr(644,root,root) %{prefix}/ESAConfig/conf/mainCfg.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/log4jFmAgent.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/log4jMasterAgent.xml
%config %attr(600,root,root) %{prefix}/ESAConfig/conf/log4jPmAgent.xml
%config %attr(755,root,mpc) %{prefix}/ESAConfig/HW/config/hw_monitors.cfg
%config %attr(755,root,mpc) %{prefix}/ESAConfig/HW/TrapTranslations/hw_alarmtrans.xml
%config %attr(755,root,mpc) %{prefix}/ESAConfig/HW/AlarmDefinitions/hw_alarmdef.xml
%config %attr(755,root,mpc) %{prefix}/ESAConfig/MPS_AlarmDefinition/GMPC_alarmdefinition.xml
%config %attr(755,root,mpc) %{prefix}/ESAConfig/MPS_AlarmDefinition/SMPC_alarmdefinition.xml
%config %attr(755,root,mpc) %{prefix}/ESAConfig/MPS_AlarmDefinition/AECID_alarmdefinition.xml
%config %attr(755,root,root) %{prefix}/ESAConfig/scripts/esa_log.py
%config %attr(755,root,root) %{prefix}/ESAConfig/scripts/esa_cluster_handler.py
%config %attr(755,root,root) %{prefix}/ESAConfig/scripts/esa_state_handler.py
%config %attr(755,root,root) %{prefix}/ESAConfig/scripts/update_alarm_handler.py
%config %attr(755,root,mpc) %{prefix}/ESAConfig/MPS_AlarmDefinition/MCN_alarmdefinition.xml
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_aecid.json
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_check.json
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_gmpc.json
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_nodes.json
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_smpc.json
%config %attr(755,root,root) %{prefix}/ESAConfig/consul/esa_config_hw.json
%config(noreplace) %attr(755,root,mpc) /var/ESA/AlarmService/log/alarms.log
%{TARGET_DIR}
%exclude %{prefix}/ESAConfig/PM
/opt/ESA
/opt/ESA/ESA
/opt/ESA/SSM/config/hw_monitors.cfg
/usr/local/esa/conf/fmAlarmDefinitions/hw_alarmdef.xml
/usr/local/esa/conf/fmAlarmTranslations/hw_alarmtrans.xml

%pre
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}

%post
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}


################################################################
# esa
################################################################
%triggerin -- esa 
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}

ESABINPATH="/opt/ESA/ESA/bin"
ESAHOME="/opt/ESA"
ESALOGHOME="/var/ESA"

$ESABINPATH/esama stop 
$ESABINPATH/esafma stop
$ESABINPATH/esapma stop

link_cfg_triggerin $ESAHOME/ESA/conf/mainCfg.xml /opt-mpc/ESAConfig/conf/mainCfg.xml
link_cfg_triggerin $ESAHOME/ESA/conf/log4jFmAgent.xml /opt-mpc/ESAConfig/conf/log4jFmAgent.xml
link_cfg_triggerin $ESAHOME/ESA/conf/log4jMasterAgent.xml /opt-mpc/ESAConfig/conf/log4jMasterAgent.xml
link_cfg_triggerin $ESAHOME/ESA/conf/log4jPmAgent.xml /opt-mpc/ESAConfig/conf/log4jPmAgent.xml
link_cfg_triggerin $ESAHOME/ESA/conf/infoSystem.xml /opt-mpc/ESAConfig/conf/infoSystem.xml
link_cfg_triggerin $ESAHOME/ESA/conf/trapDestCfg.xml /opt-mpc/ESAConfig/conf/trapDestCfg.xml
link_cfg_triggerin $ESAHOME/ESA/conf/communityCfg.xml /opt-mpc/ESAConfig/conf/communityCfg.xml
link_cfg_triggerin $ESAHOME/ESA/conf/vacmCfg.xml /opt-mpc/ESAConfig/conf/vacmCfg.xml

USER_INPUT_TRAPDEST_1_HOST=${USER_INPUT_TRAPDEST_1_HOST:-127.0.0.1}
USER_INPUT_TRAPDEST_1_PORT=${USER_INPUT_TRAPDEST_1_PORT:-162}
USER_INPUT_TRAPDEST_1_COMM_RW=${USER_INPUT_TRAPDEST_1_COMM_RW:-SNOS-PE}
USER_INPUT_TRAPDEST_1_COMM_RO=${USER_INPUT_TRAPDEST_1_COMM_RO:-SNOS-PC}

if [ "X$SNMP_VERSION" = "XV2" ]; then
	V2C_ACTIVE="yes"
	V3_ACTIVE="no"
else
	V2C_ACTIVE="no"
	V3_ACTIVE="yes"
fi

INSTALL_OMCENTER=`/bin/grep "^\s*Install_OMCenter=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`

if [ "X$INSTALL_OMCENTER" = "Xy" ]; then
	sed -i -e "s/master=\".*\" seedNodes/master=\"yes\" seedNodes/g" \
      	-e "s/ma active=\".*\"/ma active=\"yes\"/g" \
        /opt-mpc/ESAConfig/conf/mainCfg.xml
fi
      	
sed -i -e "s/\[SYSTEM_VENDOR\]/${SYSTEM_VENDOR}/g" \
	-e "s/\[SYSTEM_NAME\]/${SYSTEM_NAME}/g" \
	-e "s/\[SYSTEM_ABB_NAME\]/${SYSTEM_ABB_NAME}/g" \
	-e "s/\[SYSTEM_VERSION\]/${SYSTEM_VERSION}/g" \
	/opt-mpc/ESAConfig/conf/infoSystem.xml

sed -i -e "s/\[V2C_ACTIVE\]/${V2C_ACTIVE}/g" \
	-e "s/\[V3_ACTIVE\]/${V3_ACTIVE}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_HOST\]/${USER_INPUT_TRAPDEST_1_HOST}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_PORT\]/${USER_INPUT_TRAPDEST_1_PORT}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_COMM_RW\]/${USER_INPUT_TRAPDEST_1_COMM_RW}/g" \
	/opt-mpc/ESAConfig/conf/trapDestCfg.xml

sed -i -e "s/\[USER_INPUT_TRAPDEST_1_COMM_RO\]/${USER_INPUT_TRAPDEST_1_COMM_RO}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_COMM_RW\]/${USER_INPUT_TRAPDEST_1_COMM_RW}/g" \
	/opt-mpc/ESAConfig/conf/communityCfg.xml

sed -i -e "s/\[USER_INPUT_TRAPDEST_1_COMM_RO\]/${USER_INPUT_TRAPDEST_1_COMM_RO}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_COMM_RW\]/${USER_INPUT_TRAPDEST_1_COMM_RW}/g" \
	/opt-mpc/ESAConfig/conf/vacmCfg.xml
#################
#update cfg end
#################

#change mod for bin folder files
chown -R root:mpc $ESAHOME
chmod -R g+x $ESAHOME
chmod -R 755 $ESAHOME/ESA/conf

#Selective install alarm by product name
rm -rf  /usr/local/esa/conf/fmAlarmDefinitions/MCN_alarmdefinition.xml
ln -s /opt-mpc/ESAConfig/MPS_AlarmDefinition/MCN_alarmdefinition.xml /usr/local/esa/conf/fmAlarmDefinitions/MCN_alarmdefinition.xml
if [ "X${PRODUCT_NAME}" = "Xgmpc" ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml
	ln -s /opt-mpc/ESAConfig/MPS_AlarmDefinition/GMPC_alarmdefinition.xml /usr/local/esa/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml
elif [ "X${PRODUCT_NAME}" = "Xsmpc" ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml
	ln -s /opt-mpc/ESAConfig/MPS_AlarmDefinition/SMPC_alarmdefinition.xml /usr/local/esa/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml
elif [ "X${PRODUCT_NAME}" = "Xaecid" ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml
	ln -s /opt-mpc/ESAConfig/MPS_AlarmDefinition/AECID_alarmdefinition.xml /usr/local/esa/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml
fi

$ESABINPATH/esama start
$ESABINPATH/esafma start
$ESABINPATH/esapma start 

%triggerun -- esa 
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
ESAHOME="/opt/ESA"
triggerun_cfg $ESAHOME/ESA/conf/mainCfg.xml $*
triggerun_cfg $ESAHOME/ESA/conf/log4jFmAgent.xml $*
triggerun_cfg $ESAHOME/ESA/conf/log4jMasterAgent.xml $*
triggerun_cfg $ESAHOME/ESA/conf/log4jPmAgent.xml $*
triggerun_cfg $ESAHOME/ESA/conf/infoSystem.xml $*
triggerun_cfg $ESAHOME/ESA/conf/trapDestCfg.xml $*
triggerun_cfg $ESAHOME/ESA/conf/communityCfg.xml $*
triggerun_cfg $ESAHOME/ESA/conf/vacmCfg.xml $*

#$2 is the target rpm number
#0 = uninstall, 1 = upgrade
if [ $2 -eq 0 ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml
    rm -f /usr/local/esa/conf/fmAlarmDefinitions/MCN_alarmdefinition.xml
fi

%triggerpostun -- esa 
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
ESAHOME="/opt/ESA"
triggerpostun_cfg $ESAHOME/ESA/conf/mainCfg.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/log4jFmAgent.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/log4jMasterAgent.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/log4jPmAgent.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/infoSystem.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/trapDestCfg.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/communityCfg.xml $*
triggerpostun_cfg $ESAHOME/ESA/conf/vacmCfg.xml $*

#$2 is the target rpm number
#0 = uninstall, 1 = upgrade
if [ $2 -eq 0 ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml
        rm -f /usr/local/esa/conf/fmAlarmDefinitions/MCN_alarmdefinition.xml
fi

################################################################
# SSM
################################################################
%triggerin -- ssm
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}

ESAHOME="/opt/ESA"

/etc/init.d/ssmagent stop

link_cfg_triggerin $ESAHOME/SSM/config/agent.cfg /opt-mpc/ESAConfig/conf/agent.cfg
link_cfg_triggerin $ESAHOME/SSM/config/agent.state /opt-mpc/ESAConfig/conf/agent.state
link_cfg_triggerin $ESAHOME/SSM/config/hw_monitors.cfg /opt-mpc/ESAConfig/HW/config/hw_monitors.cfg

USER_INPUT_TRAPDEST_1_HOST=${USER_INPUT_TRAPDEST_1_HOST:-127.0.0.1}
USER_INPUT_TRAPDEST_1_PORT=${USER_INPUT_TRAPDEST_1_PORT:-162}
USER_INPUT_TRAPDEST_1_COMM_RW=${USER_INPUT_TRAPDEST_1_COMM_RW:-SNOS-PE}
USER_INPUT_TRAPDEST_1_COMM_RO=${USER_INPUT_TRAPDEST_1_COMM_RO:-SNOS-PC}

sed -i -e "s/\[USER_INPUT_TRAPDEST_1_COMM_RO\]/${USER_INPUT_TRAPDEST_1_COMM_RO}/g" \
	-e "s/\[USER_INPUT_TRAPDEST_1_COMM_RW\]/${USER_INPUT_TRAPDEST_1_COMM_RW}/g" \
	/opt-mpc/ESAConfig/conf/agent.cfg

#community string in the hw_monitor.cfg should be aligned with the one in agent.cfg 
sed -i -e "s/\[USER_INPUT_TRAPDEST_1_COMM_RW\]/${USER_INPUT_TRAPDEST_1_COMM_RW}/g" \
	/opt-mpc/ESAConfig/HW/config/hw_monitors.cfg

#agent.state will contain sys name during ssm installation, get the name in the orig file
SSM_SYS_NAME=`grep .1.3.6.1.2.1.1.5.0 /opt/ESA/SSM/config/agent.state.orig  | awk '{print $5}'`
sed -i -e "s/\[SSM_SYS_NAME\]/${SSM_SYS_NAME}/g" /opt-mpc/ESAConfig/conf/agent.state

/etc/init.d/ssmagent start

%triggerun -- ssm
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
ESAHOME="/opt/ESA"
triggerun_cfg $ESAHOME/SSM/config/agent.cfg $*
triggerun_cfg $ESAHOME/SSM/config/agent.state $*


%triggerpostun -- ssm
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
ESAHOME="/opt/ESA"
triggerpostun_cfg $ESAHOME/SSM/config/agent.cfg $*
triggerpostun_cfg $ESAHOME/SSM/config/agent.state $*


################################################################


################################################################
# consul
################################################################
%triggerin -- consulconfig
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
CONSULHOME="/opt/consul/script"
CONSULSCRIPTHOME="/opt/consul/script/esaconfig"
CONSULCONFIG="/opt/consul/config"

mkdir -p $CONSULSCRIPTHOME
chmod -R 755 $CONSULSCRIPTHOME
chown -R root:mpc $CONSULSCRIPTHOME

link_cfg_triggerin $CONSULSCRIPTHOME/esa_log.py /opt-mpc/ESAConfig/scripts/esa_log.py
link_cfg_triggerin $CONSULSCRIPTHOME/esa_cluster_handler.py /opt-mpc/ESAConfig/scripts/esa_cluster_handler.py
link_cfg_triggerin $CONSULSCRIPTHOME/esa_state_handler.py /opt-mpc/ESAConfig/scripts/esa_state_handler.py
link_cfg_triggerin $CONSULSCRIPTHOME/update_alarm_handler.py /opt-mpc/ESAConfig/scripts/update_alarm_handler.py

CONSULIP=`/bin/grep "^\s*LOCAL_CONSUL_IP=" /var/opt/setup/site.export | awk -F'=' '{print $2}'`
CLUSTERNAME=`/bin/grep "^\s*CLUSTER_NAME=" /var/opt/setup/site.export | awk -F'=' '{print $2}'`
MPSVERSION=`/bin/grep "^\s*VERSION=" /var/opt/setup/site.export | awk -F'=' '{print $2}'`
NODENAME=`/bin/grep "^\s*NODE_NAME=" /var/opt/setup/site.export | awk -F'=' '{print $2}'`

INSTALL_HW=`/bin/grep "^\s*Install_HW=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`

sed -i -e "s/\[VERSION\]/${MPSVERSION}/g" \
	-e "s/\[NODE\]/${NODENAME}/g" \
	-e "s/\[CLUSTER\]/${CLUSTERNAME}/g" \
	/opt-mpc/ESAConfig/consul/esa_config_hw.json
	
link_cfg_triggerin $CONSULCONFIG/esa_config_hw.json /opt-mpc/ESAConfig/consul/esa_config_hw.json

INSTALL_GMPC=`/bin/grep "^\s*Install_GMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_GMPC" = "Xy" ]; then
	sed -i -e "s/\[VERSION\]/${MPSVERSION}/g" \
      	-e "s/\[CLUSTER\]/${CLUSTERNAME}/g" \
      	/opt-mpc/ESAConfig/consul/esa_config_gmpc.json
      	
   link_cfg_triggerin $CONSULCONFIG/esa_config_gmpc.json /opt-mpc/ESAConfig/consul/esa_config_gmpc.json
fi

INSTALL_SMPC=`/bin/grep "^\s*Install_SMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_SMPC" = "Xy" ]; then
	sed -i -e "s/\[VERSION\]/${MPSVERSION}/g" \
      	-e "s/\[CLUSTER\]/${CLUSTERNAME}/g" \
      	/opt-mpc/ESAConfig/consul/esa_config_smpc.json
      	
    link_cfg_triggerin $CONSULCONFIG/esa_config_smpc.json /opt-mpc/ESAConfig/consul/esa_config_smpc.json
fi

INSTALL_AECID=`/bin/grep "^\s*Install_AECID=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_AECID" = "Xy" ]; then
	sed -i -e "s/\[VERSION\]/${MPSVERSION}/g" \
      	-e "s/\[CLUSTER\]/${CLUSTERNAME}/g" \
      	/opt-mpc/ESAConfig/consul/esa_config_aecid.json
      	
    link_cfg_triggerin $CONSULCONFIG/esa_config_aecid.json /opt-mpc/ESAConfig/consul/esa_config_aecid.json
fi

link_cfg_triggerin $CONSULCONFIG/esa_config_nodes.json /opt-mpc/ESAConfig/consul/esa_config_nodes.json

sed -i -e "s/\[CONSUL\]/${CONSULIP}/g" \
  	/opt-mpc/ESAConfig/consul/esa_config_check.json

link_cfg_triggerin $CONSULCONFIG/esa_config_check.json /opt-mpc/ESAConfig/consul/esa_config_check.json
consul reload

%triggerun -- consulconfig
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
CONSULHOME="/opt/consul/script"
CONSULSCRIPTHOME="/opt/consul/script/esaconfig"
CONSULCONFIG="/opt/consul/config"


triggerpostun_cfg $CONSULSCRIPTHOME/esa_log.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/esa_cluster_handler.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/esa_state_handler.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/update_alarm_handler.py $*
triggerpostun_cfg $CONSULCONFIG/esa_config_check.json $*
triggerpostun_cfg $CONSULCONFIG/esa_config_nodes.json $*
triggerpostun_cfg $CONSULCONFIG/esa_config_hw.json $*
INSTALL_GMPC=`/bin/grep "^\s*Install_GMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_GMPC" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_gmpc.json $*
fi

INSTALL_SMPC=`/bin/grep "^\s*Install_SMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_SMPC" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_smpc.json $*
fi

INSTALL_AECID=`/bin/grep "^\s*Install_AECID=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_AECID" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_aecid.json $*
fi

rm -rf $CONSULSCRIPTHOME

%triggerpostun -- consulconfig
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
CONSULHOME="/opt/consul/script"
CONSULSCRIPTHOME="/opt/consul/script/esaconfig"
CONSULCONFIG="/opt/consul/config"

triggerpostun_cfg $CONSULSCRIPTHOME/esa_log.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/esa_cluster_handler.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/esa_state_handler.py $*
triggerpostun_cfg $CONSULSCRIPTHOME/update_alarm_handler.py $*
triggerpostun_cfg $CONSULCONFIG/esa_config_check.json $*
triggerpostun_cfg $CONSULCONFIG/esa_config_nodes.json $*
triggerpostun_cfg $CONSULCONFIG/esa_config_hw.json $*

INSTALL_GMPC=`/bin/grep "^\s*Install_GMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_GMPC" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_gmpc.json $*
fi

INSTALL_SMPC=`/bin/grep "^\s*Install_SMPC=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_SMPC" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_smpc.json $*
fi

INSTALL_AECID=`/bin/grep "^\s*Install_AECID=" /var/opt/setup/install_parameters | awk -F'=' '{print $2}'`
if [ "X$INSTALL_AECID" = "Xy" ]; then
	triggerpostun_cfg $CONSULCONFIG/esa_config_aecid.json $*
fi

sed -i -e "s/master=\".*\" seedNodes/master=\"no\" seedNodes/g" \
       -e "s/ma active=\".*\"/ma active=\"no\"/g" \
        /opt-mpc/ESAConfig/conf/mainCfg.xml
        
rm -rf $CONSULSCRIPTHOME


################################################################

%preun
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}



%postun
. /opt-mpc/Config/bin/comm_functions.sh %{name}-%{version}
ESAHOME="/opt/ESA"
postun_cfg $ESAHOME/ESA/conf/mainCfg.xml
postun_cfg $ESAHOME/ESA/conf/log4jFmAgent.xml
postun_cfg $ESAHOME/ESA/conf/log4jMasterAgent.xml
postun_cfg $ESAHOME/ESA/conf/log4jPmAgent.xml
postun_cfg $ESAHOME/ESA/conf/infoSystem.xml 
postun_cfg $ESAHOME/ESA/conf/trapDestCfg.xml 
postun_cfg $ESAHOME/ESA/conf/communityCfg.xml 
postun_cfg $ESAHOME/ESA/conf/vacmCfg.xml 
postun_cfg $CONSULSCRIPTHOME/esa_log.py
postun_cfg $CONSULSCRIPTHOME/esa_cluster_handler.py
postun_cfg $CONSULSCRIPTHOME/esa_state_handler.py
postun_cfg $CONSULSCRIPTHOME/update_alarm_handler.py
postun_cfg $ESAHOME/SSM/config/agent.cfg 
postun_cfg $ESAHOME/SSM/config/agent.state 

consul reload
#0 = uninstall, 1 = upgrade
if [ $1 -eq 0 ];then
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/GMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/SMPC_alarmdefinition.xml
	rm -f /usr/local/esa/conf/fmAlarmDefinitions/AECID_alarmdefinition.xml
    rm -f /usr/local/esa/conf/fmAlarmDefinitions/MCN_alarmdefinition.xml
fi
