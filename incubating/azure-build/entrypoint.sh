#!/bin/sh
set -e

msg() { echo -e "INF---> $1"; }
err() { echo -e "ERR---> $1" ; exit 1; }

if [ "$AUTH" = "service-principal" ]
then
  az login --service-principal -u $APP_ID -p $PASSWORD --tenant $TENANT >/dev/null
else
  az login -u $USER -p $PASSWORD
fi

az acr build --registry $ACR_NAME --image $IMAGE:$TAG --file ${DOCKERFILE_PATH:-Dockerfile} $CF_VOLUME_PATH/$CF_REPO_NAME/

echo AZURE_IMAGE=$ACR_NAME.azurecr.io/$IMAGE:$TAG >> $CF_VOLUME_PATH/env_vars_to_export
