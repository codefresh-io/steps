*** Settings ***
Documentation     Tests to verify functionality of ACTION=auth
Library           Collections
Library           lib/CFStepHelm.py

*** Test Cases ***
# 255 is a custom code we have for the "Source with env and check for var" command
Sourcing will provide exported environment variables
    &{env}=   Create dictionary
    Set to dictionary   ${env}  DRY_RUN   true
    Set to dictionary   ${env}  ACTION   auth
    Set to dictionary   ${env}  GOOGLE_APPLICATION_CREDENTIALS_JSON   {"x": "y"}

    Source with env and check for var  ${env}   GOOGLE_APPLICATION_CREDENTIALS
    Return code should be   255

    Source with env and check for var  ${env}   HELM_REPO_ACCESS_TOKEN
    Return code should be   255

    Source with env and check for var  ${env}   HELM_REPO_AUTH_HEADER
    Return code should be   255

If not sourced it will exit 0
    &{env}=   Create dictionary
    Set to dictionary   ${env}  DRY_RUN   true
    Set to dictionary   ${env}  ACTION   auth

    Run with env   ${env}
    Return code should be   0
