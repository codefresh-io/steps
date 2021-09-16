#!/bin/sh
# Query the Codefresh Helm Repository for the specified version of the specified chart.
# See step.yaml for full documentation of the arguments.

# Verify required env var from pipeline
if [ -z ${CF_API_KEY+x} ] || [ -z ${CF_CTX_CF_HELM_DEFAULT_URL+x} ]; then
    echo
    echo "Required variables are missing, please import CF_HELM_DEFAULT shared config into the pipeline variables"
    exit 1
fi

# Suppress helm warnings about group-accessible kubeconfig
chmod 600 $KUBECONFIG

# Set token var for cm:// helm repo protocol
export HELM_REPO_ACCESS_TOKEN=${CF_API_KEY}

echo
echo Adding Codefresh Helm Repo \'${CF_CTX_CF_HELM_DEFAULT_URL}\'...
helm repo add codefresh ${CF_CTX_CF_HELM_DEFAULT_URL}
helm repo update
helm repo list

echo
echo Querying Helm Chart Repo...
# The grep filters out substring matches.
helm search repo codefresh/${CHART_NAME} --version ${CHART_VERSION} \
    | grep "^codefresh/${CHART_NAME}\t" \
    && export RESULT=$? \
    || export RESULT=$?

# Output results
echo
if [ $RESULT -eq 0 ]; then
    echo "Version $CHART_VERSION of chart $CHART_NAME was found in the Helm Repo"
    export CHART_VER_FOUND=true
else
    echo "Version $CHART_VERSION of chart $CHART_NAME was not found in the Helm Repo"
    export CHART_VER_FOUND=false
fi
cf_export CHART_VER_FOUND
if [ "$FAIL_WHEN" == "$CHART_VER_FOUND" ]; then 
    echo
    echo "$FAIL_WHEN_MESSAGE"
    exit 1
fi
