#!/bin/bash

for reqVar in IMAGE_NAME_TAG REGISTRY_HOSTNAME R_USER R_PASSWORD; do
    if [ -z ${!reqVar} ]; then echo "The variable $reqVar is not set, stopping..."; exit 1; fi
done

if [ ! -z $WORKING_DIRECTORY ]; then
    cd $WORKING_DIRECTORY
fi

if [ -z $DOCKERFILE ]; then
    DOCKERFILE=./Dockerfile
fi

sed -i s/_usr/$R_USER/g /makisu-internal/registry-conf.yml
sed -i s/_passwd/$R_PASSWORD/g /makisu-internal/registry-conf.yml
sed -i s/_registry_host/$REGISTRY_HOSTNAME/g /makisu-internal/registry-conf.yml

if [ -z $MAKISU_COMMAND ]; then
    MAKISU_COMMAND="makisu build -t $IMAGE_NAME_TAG -f $DOCKERFILE --storage /codefresh/volume/makisu --commit=explicit --registry-config=/makisu-internal/registry-conf.yml --push $REGISTRY_HOSTNAME --load --modifyfs=true $CUSTOM_FLAGS ."
fi

echo -e "\nRunning makisu build command:\n $MAKISU_COMMAND\n"
eval $MAKISU_COMMAND    