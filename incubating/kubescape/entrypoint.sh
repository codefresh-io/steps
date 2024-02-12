#!/busybox/sh

# Checks if `string` contains `substring`.
#
# Arguments:
#   String to check.
#
# Returns:
#   0 if `string` contains `substring`, otherwise 1.
contains() {
  case "$1" in
    *$2*) return 0 ;;
    *) return 1 ;;
  esac
}

set -e

# Kubescape uses the client name to make a request for checking for updates
export KS_CLIENT="codefresh"

if [ -n "${FRAMEWORKS}" ] && [ -n "${CONTROLS}" ]; then
  echo "Framework and Control are specified. Please specify either one of them"
  exit 1
fi

if [ -z "${FRAMEWORKS}" ] && [ -z "${CONTROLS}" ] && [ -z "${IMAGE}" ]; then
  echo "Neither Framework, Control nor image are specified. Please specify one of them"
  exit 1
fi


if [ -n "${FRAMEWORKS}" ] && [ -n "${IMAGE}" ] || [ -n "${CONTROLS}" ] && [ -n "${IMAGE}" ] ; then
  errmsg="Image and Framework / Control are specified. Kubescape does not support scanning both at the moment."
  errmsg="${errmsg} Please specify either one of them or neither."
  echo "${errmsg}"
  exit 1
fi

if [ -n "${IMAGE}" ] && [ "${FIXFILES}" = "true" ]; then
  errmsg="The run requests both an image scan and file fix suggestions. Kubescape does not support fixing image scan results at the moment."
  errmsg="${errmsg} Please specify either one of them or neither."
  echo "${errmsg}"
  exit 1
fi

# Split the controls by comma and concatenate with quotes around each control
if [ -n "${CONTROLS}" ]; then
  controls=""
  set -f
  IFS=','
  set -- "${CONTROLS}"
  set +f
  unset IFS
  for control in "$@"; do
    control=$(echo "${control}" | xargs) # Remove leading/trailing whitespaces
    controls="${controls}\"${control}\","
  done
  controls=$(echo "${controls%?}")
fi

frameworks_cmd=$([ -n "${FRAMEWORKS}" ] && echo "framework ${FRAMEWORKS}" || echo "")
controls_cmd=$([ -n "${CONTROLS}" ] && echo control "${controls}" || echo "")

scan_input=$([ -n "${FILES}" ] && echo "${FILES}" || echo .)

output_formats="${FORMAT}"
have_json_format="false"
if [ -n "${output_formats}" ] && contains "${output_formats}" "json"; then
  have_json_format="true"
fi

verbose=""
if [ -n "${VERBOSE}" ] && [ "${VERBOSE}" != "false" ]; then
  verbose="--verbose"
fi

exceptions=""
if [ -n "$EXCEPTIONS" ]; then
  exceptions="--exceptions ${EXCEPTIONS}"
fi

controls_config=""
if [ -n "$CONTROLSCONFIG" ]; then
  controls_config="--controls-config ${CONTROLSCONFIG}"
fi

should_fix_files="false"
if [ "${FIXFILES}" = "true" ]; then
  should_fix_files="true"
fi

# If a user requested Kubescape to fix their files, but forgot to ask for JSON
# output, do it for them
if [ "${should_fix_files}" = "true" ] && [ "${have_json_format}" != "true" ]; then
  output_formats="${output_formats},json"
fi

output_file=$([ -n "${OUTPUTFILE}" ] && echo "${OUTPUTFILE}" || echo "results")

account_opt=$([ -n "${ACCOUNT}" ] && echo --account "${ACCOUNT}" || echo "")
access_key_opt=$([ -n "${ACCESSKEY}" ] && echo --access-key "${ACCESSKEY}" || echo "")
server_opt=$([ -n "${SERVER}" ] && echo --server "${SERVER}" || echo "")

# If account ID is empty, we load artifacts from the local path, otherwise we
# load from the cloud (this will enable custom framework support)
artifacts_path="/home/ks/.kubescape"
artifacts_opt=$([ -n "${ACCOUNT}" ] && echo "" || echo --use-artifacts-from "${artifacts_path}")

if [ -n "${FAILEDTHRESHOLD}" ] && [ -n "${COMPLIANCETHRESHOLD}" ]; then
  echo "Both failedThreshold and complianceThreshold are specified. Please specify either one of them or neither"
  exit 1
fi

fail_threshold_opt=$([ -n "${FAILEDTHRESHOLD}" ] && echo --fail-threshold "${FAILEDTHRESHOLD}" || echo "")
compliance_threshold_opt=$([ -n "${COMPLIANCETHRESHOLD}" ] && echo --compliance-threshold "${COMPLIANCETHRESHOLD}" || echo "")

# When a user requests to fix files, the action should not fail because the
# results exceed severity. This is subject to change in the future.
severity_threshold_opt=$(
  [ -n "${SEVERITYTHRESHOLD}" ] &&
    [ "${should_fix_files}" = "false" ] &&
    echo --severity-threshold "${SEVERITYTHRESHOLD}" ||
    echo ""
)

# Handle image scanning request
image_subcmd=""
echo "image is <${IMAGE}>"
if [ -n "${IMAGE}" ]; then

  # By default, assume we are not authenticated. This means we can pull public
  # images from the container runtime daemon
  image_arg="${IMAGE}"

  severity_threshold_opt=$(
    [ -n "${SEVERITYTHRESHOLD}" ] &&
      echo --severity-threshold "${SEVERITYTHRESHOLD}" ||
      echo ""
  )

  auth_opts=""
  if [ -n "${REGISTRYUSERNAME}" ] && [ -n "${REGISTRYPASSWORD}" ]; then
    auth_opts="--username=${REGISTRYUSERNAME} --password=${REGISTRYPASSWORD}"

    # When trying to authenticate, we cannot assume that the runner has access
    # to an *authenticated* container runtime daemon, so we should always try
    # to pull images from the registry
    image_arg="registry://${image_arg}"
  else
    echo "NOTICE: Received no registry credentials, pulling without authentication."
    printf "Hint: If you provide credentials, make sure you include both the username and password.\n\n"
  fi

  # Build the image scanning subcommand with options
  image_subcmd="image ${auth_opts}"
  # Override the scan input
  scan_input="${image_arg}"
  echo "Scan subcommand: ${image_subcmd}"
fi

# TODO: include artifacts_opt once https://github.com/kubescape/kubescape/issues/1040 is resolved
scan_command="kubescape scan ${image_subcmd} ${frameworks_cmd} ${controls_cmd} ${scan_input} ${account_opt} ${access_key_opt} ${server_opt} ${fail_threshold_opt} ${compliance_threshold_opt} ${severity_threshold_opt} --format ${output_formats} --output ${output_file} ${verbose} ${exceptions} ${controls_config}"

echo "${scan_command}"
eval "${scan_command}"

if [ "$should_fix_files" = "true" ]; then
  fix_command="kubescape fix --no-confirm ${output_file}.json"
  eval "${fix_command}"
fi
