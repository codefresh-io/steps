*** Settings ***
Documentation     Tests to verify required sets of env vars
Library           Collections
Library           lib/CFStepHelm.py

*** Test Cases ***
Crashes if missing CHART_REF or CHART_NAME
    &{env}=   Create dictionary
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have failed

Will not crash if has one of CHART_REF or CHART_NAME
    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_REF   mychartref
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have succeeded

    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_NAME   mychartname
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have succeeded

Will use CHART_REF over CHART_NAME if both are provided
    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_REF   mychartref
    Set to dictionary   ${env}  CHART_NAME   mychartname
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have succeeded
    Output contains   mychartref

Crashes if missing RELEASE_NAME (ACTION=install)
    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_REF   mychartref
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have failed

Crashes if missing KUBE_CONTEXT (ACTION=install)
    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_REF   mychartref
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have failed

KUBE_CONTEXT var is required if ACTION=auth
    &{env}=   Create dictionary
    Set to dictionary   ${env}  ACTION   auth
    Set to dictionary   ${env}  KUBE_CONTEXT   helm
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have succeeded

Default ACTION is install
    &{env}=   Create dictionary
    Set to dictionary   ${env}  CHART_REF   mychartref
    Set to dictionary   ${env}  RELEASE_NAME   my-release
    Set to dictionary   ${env}  KUBE_CONTEXT   my-context
    Set to dictionary   ${env}  DRY_RUN   true
    Run with env   ${env}
    Should have succeeded
    Output contains   helm upgrade


