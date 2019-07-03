#!/bin/sh
set -e
#### Prepare functions for prettier output
msg()  { echo -e "\e[32mINFO [$(date +%F_%H-%M-%S)] ---> $1\e[0m"; }
warn() { echo -e "\e[33mWARN [$(date +%F_%H-%M-%S)] ---> $1\e[0m"; }
err()  { echo -e "\e[31mERR  [$(date +%F_%H-%M-%S)] ---> $1\e[0m" ; exit 1; }

msg "Running codefresh plugin $CF_PLUGIN_NAME"

msg "Scanning image with Anchore"
anchore-cli image add ${ANCHORE_CLI_IMAGE}
msg "Waiting for analysis to complete"
anchore-cli image wait ${ANCHORE_CLI_IMAGE}
msg "Analysis complete"
 if [ "${ANCHORE_FAIL_ON_POLICY}" == "true" ] ; then 
   anchore-cli evaluate check ${ANCHORE_CLI_IMAGE}; 
fi
