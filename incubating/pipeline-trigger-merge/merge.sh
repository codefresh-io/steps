#!/bin/bash

process_dir() {
  echo  "Processing trigger directory $1"
  for FILE in $1/* ; do
    process_file $FILE
  done
}

process_file() {
  if [ -f $1 ]; then
    echo  "Processing trigger file $1"
    if [ $count -eq 1 ] ; then
      yq -s -y '.[0].spec.triggers = [.[1].spec.triggers | add] | .[0]' $curdir/$SPEC $1 > $CF_BUILD_ID.yml
    else
      yq -s -y '.[0].spec.triggers = [.[].spec.triggers |.[]] | .[0]' $curdir/$SPEC $1 > $CF_BUILD_ID.yml
    fi
    mv $CF_BUILD_ID.yml $curdir/$SPEC
    count=$(expr $count + 1)
    return
  fi
  if [ -d $1 ] ; then
    process_dir $1
    return
  fi
  echo "WARNING: Unknown trigger file $1"
}

# exit on error
set -e
echo "pipeline-trigger-merge v1.1.0"

count=1
echo "Merging pipeline spec $SPEC with triggers $TRIGGERS"
for f in `echo $TRIGGERS` ; do
    # is path absolute
    if [[ "$f" = /* ]] ; then
      curdir="/"
    else
      curdir=`pwd`
    fi
    process_file $f
done

echo "Creating/Updating final pipeline"

# Get pipeline name
echo "Checking if pipeline already exists"
name=$(yq '.metadata.name' $SPEC)
codefresh get pip $name > pipeline.log 2>&1 || true

#Check if pipeline exists
if [ `grep -c PIPELINE_NOT_FOUND pipeline.log` -eq 0 ] ; then
  echo "Updating final pipeline"
  cmd="codefresh replace -f $SPEC"
else
  echo "Creating final pipeline"
  cmd="codefresh create pipeline -f $SPEC"
fi

# Check for error when creating/updating the pipeline
echo "Checking for errors"
$cmd 2>&1 | tee pipeline.log
exit `grep -c 'Yaml validation errors' pipeline.log`
