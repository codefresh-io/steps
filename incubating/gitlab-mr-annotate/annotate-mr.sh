#!/bin/bash

# check if the required vars are set
for reqVar in CF_PULL_REQUEST_ID CF_REPO_OWNER CF_REPO_NAME CF_API_KEY GIT_CONTEXT LABELS; do
    if [ -z ${!reqVar} ]; then echo "The variable $reqVar is not set, stopping..."; exit 1; fi
done

# set default values for some of the env vars
if [ -z $MERGE_REQUEST_ID ]; then MERGE_REQUEST_ID=$CF_PULL_REQUEST_ID; fi
if [ -z $PROJECT_ID ]; then PROJECT_ID="$CF_REPO_OWNER%2F$CF_REPO_NAME"; fi
# TO DO: write a function for getting default git context and setting it as a default value for GIT_CONTEXT variable

function getAccessToken {
    GITLAB_ACCESS_TOKEN=$(curl -s -H "x-access-token: $CF_API_KEY" https://g.codefresh.io/api/contexts/$GIT_CONTEXT?decrypt=true | jq .spec.data.auth.password --raw-output)
}

function setAuthHeader {
    getAccessToken
    AUTH_METHOD=$(curl -s -H "x-access-token: $CF_API_KEY" https://g.codefresh.io/api/contexts/$GIT_CONTEXT?decrypt=true | jq .spec.data.auth.type --raw-output)
    if [ $AUTH_METHOD == "basic" ]; then AUTH_HEADER="Private-Token: $GITLAB_ACCESS_TOKEN"; else AUTH_HEADER="Authorization: Bearer $GITLAB_ACCESS_TOKEN"; fi
}

function annotateMR {
    STATUS=$(curl -I -s -X PUT --header "$AUTH_HEADER" https://gitlab.com/api/v4/projects/$PROJECT_ID/merge_requests/$MERGE_REQUEST_ID?labels=$LABELS)
    if [[ $(echo $STATUS | grep '200 OK') ]]; then
        echo "The MR has been successfully updated"
    else
        echo "MR update has failed"
        echo "The response: $STATUS"
    fi
}

setAuthHeader
annotateMR
