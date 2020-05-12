#!/bin/sh
set -e

#Initialize build_number annotation variable
annotation_variable='build_number'

# Grab the current build information and output to json
printf '\nBuild ID: %s' "$CF_BUILD_ID"

if [ "$ANNOTATION_NAME" = '${{ANNOTATION_NAME}}' ]
then
    printf '\n\nANNOTATION_PREFIX is empty. Annotation name will be build_number'
else
    printf '\n\nAnnotation name passed in: %s' "$ANNOTATION_NAME"
    annotation_variable="$ANNOTATION_NAME"
fi

printf '\n\nCurrent build JSON\n'
codefresh get build $CF_BUILD_ID -o json

# Use jq to traverse the json and grab the pipeline id
pipelineid=$(codefresh get build $CF_BUILD_ID -o json | jq '."pipeline-Id"')
printf '\nJSON parsed pipeline-Id: %s \n' "$pipelineid"

# If the annotation build_number already exists, increment it by 1
# If the annotation build_number doesn't exist, initialize it at 1
printf '\nGet annotation JSON value using jq\n'
build_number=$(codefresh get annotation pipeline $pipelineid $annotation_variable -o json | jq '.value' -j) || true
printf '\nCurrent value: %s' "$build_number"
new_build_number=$((build_number+1))

printf '\nBumped value: %s \n' "$new_build_number"
printf '\nCreating annotation: '
codefresh create annotation pipeline $pipelineid $annotation_variable=$new_build_number

printf '\nUpdated annotation build_number JSON\n'
codefresh get annotation pipeline $pipelineid $annotation_variable -o json

printf '\nExporting build number to CF_BUILD_NUMBER\n'
echo CF_BUILD_NUMBER="$new_build_number" >> env_vars_to_export