#!/usr/bin/env bash

set -e
set -o pipefail

# DATE=$(date +%F)
# CACHE_DIR="/codefresh/volume/.trivy"
CACHE_DIR="~/.trivy"
# REPORT_DIR="${TRIVY_DIR}/reports"
# TRIVY_OUTPUT_FILE=${TRIVY_OUTPUT_FILE:-`echo ${REPORT_DIR}/report-${DATE}.json`}
TRIVY_IGNOREFILE="/tmp/.trivyignore" # default
# TRIVY_IGNORE_FILE # set as a step parameter


function echoSection {
  printf -- "--------------------------------------------\n\n"
  printf  "\n\n[INFO] $1\n\n"
}

unset_empty_vars() {
  echoSection "Unsetting empty vars"
  for var in $(env); do 
    if [[ "${var##*=}" == "\${{${var%=*}}}" ]]; then 
      echo "Unsetting ${var%=*}"; 
      unset ${var%=*};
    fi;
  done
}

set_trivy_ignore() {
  echoSection "Set up trivy ignore file"
  echo > $TRIVY_IGNOREFILE
  # merge from file
  if [[ ! -z $TRIVY_IGNORE_FILE ]]; then
    stat -c "%n" "$TRIVY_IGNORE_FILE"
    cp $TRIVY_IGNORE_FILE $TRIVY_IGNOREFILE
  fi 
  local IFS=$',' 
  for cve in $TRIVY_IGNORE_LIST; do
    echo $cve >> $TRIVY_IGNOREFILE
  done
  echo ".trivyignore:"
  cat $TRIVY_IGNOREFILE
}

generate_images_list() {
  local IMAGES
  # merge from file
  if [[ ! -z $IMAGES_FILE ]]; then
    IMAGES=$(cat $IMAGES_FILE | tr '\n' ' ')
  fi
  # merge from list
  if [[ ! -z $IMAGES_LIST ]]; then
    IMAGES="$IMAGES $(echo $IMAGES_LIST | tr ',' ' ')"
  fi
  if [[ -z $IMAGES ]]; then
    echo "[ERROR] The list of images is empty."
    exit 1
  fi
  echo $IMAGES
}

scan_template() {
  local image=$1
  local object=$(trivy -q -f json --cache-dir ${CACHE_DIR} --ignorefile ${TRIVY_IGNOREFILE} ${image} | sed 's|null|\[\]|')
  count=$( echo $object | jq length)
  for ((i = 0 ; i < $count ; i++)); do
    local vuln_length=$(echo $object | jq -r --arg index "${i}" '.[($index|tonumber)].Vulnerabilities | length')
    if [[ "$vuln_length" -eq "0" ]] && [[ "$SKIP_EMPTY" == "true" ]]; then
      continue
    fi
    echo -E "\n"Target: $(echo $object | jq -r --arg index "${i}" '.[($index|tonumber)].Target')
    echo "..."
    echo $object | jq -r --arg index "${i}" '.[($index|tonumber)].Vulnerabilities[] | "\(.PkgName) \(.VulnerabilityID) \(.Severity)"' | column -t | sort -k3
  done
}

slack_image_section() {
  local image=$1
  local header="*${image}*"
  local body=$(scan_template $image | awk '{print}' ORS='\\n')
  if [[ -z $body ]]; then return; fi
  echo -E "{
  \"type\": \"section\",
  \"text\": {
    \"type\": \"mrkdwn\",
    \"text\": \"${header}\n\`\`\`${body}\`\`\` \"
  }
}
"
}

# MAIN
main() {

  unset_empty_vars

  set_trivy_ignore

  if [[ ! -d "$CACHE_DIR" ]]; then
    mkdir -p ${CACHE_DIR}
  fi

  echoSection "Update trivy DB"
  trivy --download-db-only --cache-dir ${CACHE_DIR}

  SLACK_REPORT_MESSAGE='{"blocks":[]}'

  local images=$(generate_images_list)
  echoSection "List of images: ${images}"

  for cfimage in $images; do
    echoSection "Scanning $cfimage image"
    local section=$(slack_image_section "$cfimage")
    if [[ ! -z $section ]]; then
      SLACK_REPORT_MESSAGE=$( jq --argjson insert "${section}" '.blocks[.blocks|length] |= .+ $insert' <<< "$SLACK_REPORT_MESSAGE" )
      SLACK_REPORT_MESSAGE=$( jq '.blocks[.blocks|length] |= .+ {"type": "divider"}' <<< "$SLACK_REPORT_MESSAGE" )
    fi
  done

 if [[ "$(echo $SLACK_REPORT_MESSAGE | jq '[.blocks[] | select(.type == "section")] | length' )" -eq "0" ]]; then
   echoSection "The list of vulnerabilities is empty. Nothing to send."
 else
   curl -X POST -H "Content-type: application/json" ${SLACK_INCOMING_URL} --data "$SLACK_REPORT_MESSAGE"
 fi
}

main $@

