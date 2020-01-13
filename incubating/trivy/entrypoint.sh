#!/usr/bin/env bash

set -e
set -o pipefail

# TODO
# clear cache because of 'latest' images

DATE=$(date +%F)
TRIVY_DIR="/codefresh/volume/trivy"
CACHE_DIR="${TRIVY_DIR}/cache"
REPORT_DIR="${TRIVY_DIR}/reports"
TRIVY_OUTPUT=${TRIVY_OUTPUT:-`echo ${REPORT_DIR}/report-${DATE}.json`}
TRIVY_IGNOREFILE=${TRIVY_IGNOREFILE:-${TRIVY_DIR}/.trivyignore}

echoSection() {
  printf -- "--------------------------------------------\n\n"
  printf  "\n\n[INFO] $1\n\n"
}

scan_image() {
# TODO
# to catch  GitHub 'API rate limit exceeded' error
  local image=$1
  local format=${2:-table}
  trivy \
    -f ${format} \
    -q \
    --ignore-unfixed \
    --cache-dir ${CACHE_DIR} \
    --skip-update \
    $image
}

set_trivy_ignore() {
  echoSection "Set up trivy ignore file"
  local IFS=$',' 
  for cve in $TRIVY_IGNORE_LIST; do
    echo $cve >> $TRIVY_IGNOREFILE
  done
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

main() {
# Check images list
  if [[ -z $IMAGES_LIST ]]; then
    echo "[ERROR] The \$IMAGES_LIST variable is empty."
    exit 1
  fi

  unset_empty_vars

  set_trivy_ignore

  echoSection "Create report dir"
  if [[ ! -d "$REPORT_DIR" ]]; then
    mkdir -p ${REPORT_DIR}
  fi

  echoSection "Create the main report file"
  echo '{"IMAGES": {}}' | jq . > ${TRIVY_OUTPUT}

  echoSection "Update trivy DB"
  trivy --download-db-only --cache-dir ${CACHE_DIR}

  local IFS=$',' 

  for IMAGE in $IMAGES_LIST; do
    echoSection "Scanning $IMAGE image."
    scan_image $IMAGE
    echo "Get the json"
    local SCAN_OBJECT=$(scan_image $IMAGE json)
    echo "Json object: ${SCAN_OBJECT}"
    echo "Merge merge json with the main report file"
    jq \
      --arg image_name "${IMAGE}" \
      --argjson scanObject "${SCAN_OBJECT}" \
      '.IMAGES |= .+ {($image_name): $scanObject}' \
      $TRIVY_OUTPUT > /tmp/tmp.json && mv /tmp/tmp.json $TRIVY_OUTPUT
  done

  echoSection "Trivy output json file - ${TRIVY_OUTPUT}"

}

main $@
