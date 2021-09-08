#! /bin/sh
# -------------------------------------------------------------------------------------
# promote.sh
#   Promotes values between helm charts located in different directories.
#   Will update values in the values.yaml (based on user-specified IMAGE_FORMAT)
#   As well as the depdencies in the Chart.yaml
#   Additionally it will bump the Chart.yaml version to the next major, minor or patch
# =====================================================================================

# Which part of the version to bump: major, minor or patch
BUMP_VERSION="${BUMP_VERSION:-patch}"
# YAML path to the image tag
IMAGE_FORMAT="${IMAGE_FORMAT:-{{IMAGE\}\}.image.tag}"
# YAML file names with extensions
CHART_YAML="${CHART_YAML:-Chart.yaml}"
VALUES_YAML="${VALUES_YAML:-values.yaml}"


# YAML files names for promote from and to. Useful if these are ever different
FROM_CHART_YAML="${FROM_CHART_YAML:-${CHART_YAML}}"
TO_CHART_YAML="${TO_CHART_YAML:-${CHART_YAML}}"

FROM_VALUES_YAML="${FROM_VALUES_YAML:-${VALUES_YAML}}"
TO_VALUES_YAML="${TO_VALUES_YAML:-${VALUES_YAML}}"

# If chart names differ from image names, they can be set independently
PROMOTE_CHARTS="${PROMOTE_CHARTS:-${PROMOTE_IMAGES}}"

# Error formatter
function print_error() {
  echo >&2 -e "ERROR: $1"; exit "$2" || exit 1;
}

function update_chart_yaml() {
  # Not strictly needed, but more explicit
  local CHART=$1

  echo "INFO: Updating dependency in ${PROMOTE_TO}/${TO_CHART_YAML}"
  # Get the new version of the chart
  local PROMOTED_CHART_VERSION=$(yq eval '.dependencies[] | select (.name == "'${CHART}'") | .version' "${PROMOTE_FROM}/${FROM_CHART_YAML}")
  # Update Chart.y[a]ml to the new chart version
  yq eval --inplace '.dependencies[] |= select (.name == "'${CHART}'") .version="'${PROMOTED_CHART_VERSION}'"' "${PROMOTE_TO}/${TO_CHART_YAML}"
}

function update_values_yaml() {
  # Not strictly needed, but more explicit
  local IMAGE=$1

  echo "INFO: Updating value in ${PROMOTE_TO}/${TO_VALUES_YAML}"
  # Expand variables in replace string, potentially unsafe -- consider replacing
  local REPLACE_STR=$(echo ${IMAGE_FORMAT} | sed "s/{{.*}}/${IMAGE}/g")
  # Check if first char is a dot if not, make it one
  if [[ "${REPLACE_STR:0:1}" != "." ]]; then
    REPLACE_STR=".${REPLACE_STR}"
  fi

  # IF YAML formats are not the same between PROMOTE_FROM and PROMOTE_TO this will fail
  local PROMOTED_IMAGE_VERSION=$(yq eval ${REPLACE_STR} "${PROMOTE_FROM}/${FROM_VALUES_YAML}")
  yq eval --inplace ${REPLACE_STR}'="'${PROMOTED_IMAGE_VERSION}'"' "${PROMOTE_TO}/${TO_VALUES_YAML}"
}

bump_semver() {
  # adapted from https://gist.github.com/JonTheNiceGuy/57ed3ba585fba0b523cad050a2d2a5d3#file-nextver-sh
  local RE='[^0-9]*\([0-9]*\)[.]\([0-9]*\)[.]\([0-9]*\)\([0-9A-Za-z-]*\)'
  local BASE_VERSION=$1

  MAJOR=$(echo ${BASE_VERSION} | sed -e "s#$RE#\1#")
  MINOR=$(echo ${BASE_VERSION} | sed -e "s#$RE#\2#")
  PATCH=$(echo ${BASE_VERSION} | sed -e "s#$RE#\3#")

  case "${BUMP_VERSION}" in
  major)
    let MAJOR+=1
    ;;
  minor)
    let MINOR+=1
    ;;
  patch)
    let PATCH+=1
    ;;
  esac

  echo "${MAJOR}.${MINOR}.${PATCH}"
}

update_chart_version() {
  # Get chart version
  BASE_VERSION=$(yq eval '.version' "${PROMOTE_TO}/${TO_CHART_YAML}")

  # Get bumped version
  NEW_VERSION="$(bump_semver ${BASE_VERSION})"

  # Patch chart version
  yq eval --inplace '.version="'${NEW_VERSION}'"' "${PROMOTE_TO}/${TO_CHART_YAML}"

  echo "INFO: Bumped chart version from ${BASE_VERSION} to ${NEW_VERSION}"
}

function nonzero_checks() {
  # Run some checks to make sure required parameters exist
  # Make sure vars not empty
  if [[ -z "${PROMOTE_FROM}" ||  -z "${PROMOTE_TO}" ]]; then
    print_error "PROMOTE_FROM and PROMOTE_TO variables cannot be empty" 2
  fi

  # Make sure vars not equal
  if [[ "${PROMOTE_FROM}" == "${PROMOTE_TO}" ]]; then
    if [[ "${{FROM_VALUES_YAML}}" == "${{TO_VALUES_YAML}}" ]]; then
        print_error "PROMOTE_FROM and PROMOTE_TO variables cannot be equal if FROM_VALUES_YAML is equal to TO_VALUES_YAML" 4
    fi
  fi
  # Make sure dirs exist
  stat ${PROMOTE_FROM} &> /dev/null && stat ${PROMOTE_TO} &> /dev/null || (print_error "PROMOTE_FROM and PROMOTE_TO directories must both exist" 8)
}

main() {
  nonzero_checks

  # Update the chart version
  update_chart_version

  # These are in a loops -- lots of writes to the same file if updating multiple items :/ Consider a way to unravel
  # ---- UPDATE VALUES.YAML ----
  for IMAGE in ${PROMOTE_IMAGES//,/ }; do
    update_values_yaml "${IMAGE}"
  done

  # ---- UPDATE CHART.YAML ----
  for CHART in ${PROMOTE_CHARTS//,/ }; do
    update_chart_yaml "${CHART}"
  done
}

main