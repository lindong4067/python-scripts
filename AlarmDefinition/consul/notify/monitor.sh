#!/bin/sh   
#=====================  
# configuration
# Include config file istead of sed the original file
[ -r /var/opt/setup/site.export ] && . /var/opt/setup/site.export
MPC_HOME=${MPC_HOME:-/opt-mpc/MPC}
OUTPUT_LOG_DIR=${VAR_OUTPUT_LOG_DIR:-/var/opt/fds/logs} 
# the python rcommand
command="${MPC_HOME}/plugins/Utility/latest/consul/notify/main.py"
runCommand="python ${command}"

if [ "x${OUTPUT_LOG_DIR}" = "x" ]; then
    destination=">/dev/console 2>&1"
elif [ -w "${OUTPUT_LOG_DIR}" ]; then
    destination="> ${OUTPUT_LOG_DIR}/notifier.log 2>&1"
else
    destination="> /tmp/notifier.log 2>&1"
fi

function monitor()
{
while true;
do   
  echo "`date` : begin*****************" 
  stillRunning=$(ps -ef |grep -v "grep" |grep "${command}")
  echo "`date`: stillRunning=${stillRunning}" 
  if [ "$stillRunning" ] ; then   
     echo "`date`: notify service was already started."
  else   
     echo "`date`: notify service was not started"
     echo "`date`: Starting service ..."
     eval "${runCommand} ${destination} &"
  fi   
  sleep 10   
  echo "`date` : end******************"
done   
}

monitor > /dev/null 

