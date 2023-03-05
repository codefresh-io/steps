# !/bin/bash

set -o pipefail

FORBID_DECRYPT_MSG="Decrypting contexts is not allowed because 'forbidDecrypt' feature is enabled"

bold() { echo -e "\e[1m$@\e[0m" ; }
red() { echo -e "\e[31m$@\e[0m" ; }
green() { echo -e "\e[32m$@\e[0m" ; }
yellow() { echo -e "\e[33m$@\e[0m" ; }

ok() { green OK ; }

REQUIRED_VARS=(
    GIT_CONTEXT
    REPO_OWNER
    REPO_NAME
    RELEASE_TAG
    RELEASE_NAME
)

OPTIONAL_VARS=(
    GIT_TOKEN
    RELEASE_DESCRIPTION
    FILES
    DRAFT
    PRERELEASE
    BASE_URL
)

ALL_VARS=(`echo "${REQUIRED_VARS[@]}"` `echo "${OPTIONAL_VARS[@]}"`)

function getTokenFromContext() {
    bold "Getting a git token from the context \"${GIT_CONTEXT}\"..."
    GITHUB_TOKEN_RESPONSE=$(codefresh get contexts --type git.github $1 --decrypt -o json 2>&1)
    if [ $? != 0 ]; then
        red "Failed to get the git token from context \"${GIT_CONTEXT}\" with error: ${GITHUB_TOKEN_RESPONSE}"
        if [ -z "${GITHUB_TOKEN_RESPONSE##*$FORBID_DECRYPT_MSG*}" ]; then
            yellow "You should use the 'git_token' argument to pass a github token"
        fi
        return 1
    fi
    GITHUB_TOKEN=$(echo ${GITHUB_TOKEN_RESPONSE} | jq -r '.spec.data.auth.password')
    export GITHUB_TOKEN
    ok
}

function getContextFromTrigger() {
    checkTrigger || return 1
    result=$(codefresh get pipeline "$CF_PIPELINE_NAME" -o json | jq --arg triggerId "${CF_PIPELINE_TRIGGER_ID}" -r '.spec.triggers[] | select(.id == $triggerId) | .context') || return 1 
    eval $1=$result
}

function checkTrigger() {
    if [ -z "$CF_PIPELINE_TRIGGER_ID" ]; then
        red "Failed to get the trigger data - the pipeline hasn't been started by a trigger"
        yellow "If the pipeline is not started by a trigger, the arguments git_context, release_tag, repo_name and repo_owner must be set manually"
        return 1
    fi
}

function setDefaultVarValues() {
    if [ ! -z "$GIT_TOKEN" ]; then
        bold "Using git token for authentication..."
        GIT_CONTEXT="_" # This is irrelevant, we are using git_token method
        GITHUB_TOKEN="$GIT_TOKEN"
        export GITHUB_TOKEN
    fi

    if [ -z "$GIT_CONTEXT" ]; then
        yellow "GIT_CONTEXT var is not set explicitly. Trying to get it from the trigger by default..."
        getContextFromTrigger GIT_CONTEXT
        [ $? != 0 ] && return 1
        ok
    fi

    if [ -z "$RELEASE_TAG" ]; then
        yellow "RELEASE_TAG var is not set explicitly. Trying to get it from the trigger by default..."
        checkTrigger || return 1
        RELEASE_TAG="$CF_BRANCH_TAG_NORMALIZED"
        ok
    fi

    if [ -z "$REPO_OWNER" ]; then
        yellow "REPO_OWNER var is not set explicitly. Trying to get it from the trigger by default..."
        checkTrigger || return 1
        REPO_OWNER="$CF_REPO_OWNER"
        ok
    fi

    if [ -z "$REPO_NAME" ]; then
        yellow "REPO_NAME var is not set explicitly. Trying to get it from the trigger by default..."
        checkTrigger || return 1
        REPO_NAME="$CF_REPO_NAME"
        ok
    fi

    if [ "$PRERELEASE" = "true" ]; then
        PRERELEASE="-p true";
    else 
        PRERELEASE="";
    fi

    if [ "$DRAFT" = "true" ]; then
        DRAFT="-d true";
    else 
        DRAFT="";
    fi

    if [ ! -z "$BASE_URL" ]; then
        BASE_URL="--baseurl $BASE_URL";
    else 
        BASE_URL="";
    fi
}

# There might be values for cf empty vars, like ${{VAR}} substituted like this into
# the script. We want them to be really empty
function handleCfEmptyVars() {
    for var in ${ALL_VARS[*]}; do
        if ( echo "${!var}" | grep '${{' &>/dev/null ); then eval $var=""; fi
    done
}

function validateReqVars() {
    for reqVar in ${REQUIRED_VARS[*]}; do
        if [ -z ${!reqVar} ]; then echo "The variable $reqVar is not set, stopping..."; exit 1; fi
    done
}

function main() {

    handleCfEmptyVars
    setDefaultVarValues
    [ $? != 0 ] && red "Failed to set default value for one of the required variables, exiting..." && return 1

    if [ -z "$GITHUB_TOKEN" ]; then
        getTokenFromContext $GIT_CONTEXT
        [ $? != 0 ] && return 1
    fi

    validateReqVars

    if [ ! -z $FILES ]; then FILES=$(echo "$FILES" | tr "," " "); fi

    github-release upload \
        $DRAFT \
        $PRERELEASE \
        $BASE_URL \
        --token $GITHUB_TOKEN \
        --owner "$REPO_OWNER" \
        --repo "$REPO_NAME" \
        --tag "$RELEASE_TAG" \
        --name "$RELEASE_NAME" \
        --body "$RELEASE_DESCRIPTION" \
        $FILES
    
    if [ $? != 0 ]; then 
        return 1
    else
        green "Release has been successfully created/updated"
    fi

}

main
