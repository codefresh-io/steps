# Look at the previous changes in git and apply the pipeline updates to codefresh pipelines
# Takes:
#   TRIGGERS_SUBDIR - The subdirectory name where triggers would be stored
#   SPEC - The YAML file name of the pipelines spec(s)

print_error() {
  message="$1"
  echo "WARNING: ${message}"
}

print_info() {
  message="$1"
  echo "INFO: ${message}"
}

print_debug() {
  message="$1"
  if [[ "$DEBUG" == "true" ]]; then
    echo "DEBUG: ${message}"
  fi
}

update_changed_pipelines() {
  DEBUG=${DEBUG:-false}
  TRIGGERS_SUBDIR=${TRIGGERS_SUBDIR:-triggers}
  SPEC=${SPEC:-codefresh-spec.yaml}

  print_debug "Debug mode on"
  print_debug "PWD: ${PWD}"
  print_debug "ls: $(ls)"
  print_debug "SPEC=${SPEC}"
  print_debug "TRIGGERS_SUBDIR=${TRIGGERS_SUBDIR}"

  # get the directories that have changed since the last commit
  CHANGED_DIRS=$(git --no-pager log -m -1 --pretty="" --name-only | sed 's|\(.*\)/.*|\1|' | sed -e "s|\(/${TRIGGERS_SUBDIR}\)*$||g" | sort | uniq)

  print_debug "CHANGED_DIRS=${CHANGED_DIRS}"

  # Loop through the directory list
  for dir in ${CHANGED_DIRS}; do
    # Prepend directory to spec name if we are not processing the root spec
    CURR_SPEC=${SPEC}
    if [[ ${dir} != "${CURR_SPEC}" ]]; then
      CURR_SPEC="${dir}/${CURR_SPEC}"
    fi
    print_debug "CURR_SPEC=${CURR_SPEC}"

    # Make sure file exists before trying to apply it
    if [[ -f ${CURR_SPEC} ]]; then
      print_info "Updating pipeline spec: ${CURR_SPEC}"
      # If we have triggers merge them in, otherwise just apply the spec
      if [[ -d ${dir}/${TRIGGERS_SUBDIR} ]]; then
        print_debug "Running 'SPEC=${CURR_SPEC} TRIGGERS=${dir}/${TRIGGERS_SUBDIR} /merge.sh'"
        SPEC=${CURR_SPEC} TRIGGERS=${dir}/${TRIGGERS_SUBDIR} /merge.sh
      else
        print_debug "Running 'codefresh create pipeline -f ${CURR_SPEC} || codefresh replace -f ${CURR_SPEC}'"
        codefresh create pipeline -f ${CURR_SPEC} || codefresh replace -f ${CURR_SPEC}
      fi
    else
      print_error "Skipping ${CURR_SPEC}, file does not exist"
    fi
  done
}

update_changed_pipelines
