#!/bin/bash
BINTRAY_COMMAND=${BINTRAY_COMMAND:- 'ps'}
BINTRAY_LICENCES=${BINTRAY_LICENCES:- 'MIT'}
BINTRAY_ARGS=${BINTRAY_ARGS:- 'codefresh-1234/test/cf-demo'}

#Global setup
/app/jfrog bt config --user $BINTRAY_USER  --key $BINTRAY_KEY --licenses $BINTRAY_LICENCES

echo Running $BINTRAY_COMMAND with $BINTRAY_ARGS
/app/jfrog bt $BINTRAY_COMMAND $BINTRAY_ARGS 