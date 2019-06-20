#!/bin/bash

PULLS_URI=https://api.github.com/repos/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}/pulls
AUTHORIZATION_HEADER="Authorization: token ${GITHUB_TOKEN}"

GITHUB_PR_OPERATION="${GITHUB_PR_OPERATION:-create}"

error () {
    echo $1 >& 2
    exit 1
}

validate_required_params (){
    if [[ ! -n "${GITHUB_TOKEN}" ]]; then
        error 'Environment variable "GITHUB_TOKEN" is not provided!'
    fi
    if [[ ! -n "${GITHUB_REPO_OWNER}" ]]; then
        error 'Environment variable "GITHUB_REPO_OWNER" is not provided!'
    fi
    if [[ ! -n "${GITHUB_REPO_NAME}" ]]; then
        error 'Environment variable "GITHUB_REPO_NAME" is not provided!'
    fi
}

validate_create_params (){
    if [[ ! -n "${TITLE}" ]]; then
        error 'Environment variable "TITLE" is not provided!'
    fi
    if [[ ! -n "${BASE}" ]]; then
        error 'Environment variable "BASE" is not provided!'
    fi
    if [[ ! -n "${HEAD}" ]]; then
        error 'Environment variable "HEAD" is not provided!'
    fi
}

apply_patch () {
    echo ${GITHUB_PR_NUMBER}
    if [[ ! -n "${GITHUB_PR_NUMBER}" ]]; then
        error 'Environment variable "GITHUB_PR_NUMBER" is not provided!'
    fi
    BODY=$1
    METHOD=PATCH
    OPTIONAL_PR_NUMBER='/'${GITHUB_PR_NUMBER}
}

join_by () { local IFS="$1"; shift; echo "$*"; }

make_update_body () {
    local body_arr=()

    if [[ -n "${TITLE}" ]]; then
        body_arr+=('"title":"'"${TITLE}"'"')
    fi

    if [[ -n "${BASE}" ]]; then
        body_arr+=('"base":"'"${BASE}"'"')
    fi

    if [[ -n "${HEAD}" ]]; then
        body_arr+=('"head":"'"${HEAD}"'"')
    fi

    local body="$(join_by , "${body_arr[@]}")"
    echo "{ ${body} }"
}

process_command () {
    if [[ ${GITHUB_PR_OPERATION} == 'create' ]]; then
        validate_create_params
        BODY='{"title": "'"${TITLE}"'", "base": "'"${BASE}"'", "head": "'"${HEAD}"'"}'
        METHOD=POST
    elif [[ ${GITHUB_PR_OPERATION} == 'update' ]]; then
        apply_patch "$(make_update_body)"
    elif [[ ${GITHUB_PR_OPERATION} == 'open' ]]; then
        apply_patch '{"state": "open"}'
    elif [[ ${GITHUB_PR_OPERATION} == 'close' ]]; then
        apply_patch '{"state": "close"}'
    else
        error "PR_OPERATION '${GITHUB_PR_OPERATION}' is not supported!"
    fi
}

validate_required_params
process_command

echo body:
echo ${BODY}
echo

curl -H "${AUTHORIZATION_HEADER}" -X ${METHOD} -d "${BODY}" ${PULLS_URI}${OPTIONAL_PR_NUMBER}
