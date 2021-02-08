#/bin/#!/usr/bin/env bash

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
export curdir=`pwd`
export count=1
echo "Merging pipeline spec $SPEC with triggers $TRIGGERS"
for f in `echo $TRIGGERS` ; do
    process_file $f
done
echo "Creating/Updating final pipeline"
codefresh create pipeline -f $SPEC || codefresh replace -f $SPEC
