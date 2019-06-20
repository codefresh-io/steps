#!/bin/sh
set -e
#### Prepare functions for prettier output
msg()  { echo -e "\e[32mINFO [$(date +%F_%H-%M-%S)] ---> $1\e[0m"; }
warn() { echo -e "\e[33mWARN [$(date +%F_%H-%M-%S)] ---> $1\e[0m"; }
err()  { echo -e "\e[31mERR  [$(date +%F_%H-%M-%S)] ---> $1\e[0m" ; exit 1; }

msg "Running codefresh plugin $CF_PLUGIN_NAME"
#### Check for required environment variables
[ -z "$PLUGIN_RESULT" ] && err "Need to set PLUGIN_RESULT"

msg "Environment variable PLUGIN_RESULT is: ${PLUGIN_RESULT}"
msg "Codefresh account is ${CF_ACCOUNT}"
warn "Contents of your workflow directory: \n $(ls -la ${CF_VOLUME_PATH})"

if [ "$PLUGIN_RESULT" = "SUCCESS" ]; then
    msg "Requested PLUGIN_RESULT is SUCCESS. Have a great day!"
else
    err "Requested PLUGIN_RESULT is $PLUGIN_RESULT. Failing."
fi
