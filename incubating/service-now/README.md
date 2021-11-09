# ServiceNow integration

### Prerequisites:

- Codefresh Subscription - https://codefresh.io/
- ServiceNow instance with Change Management enabled. You can get a free one at https://developer.servicenow.com/
- Latest Update Set [xml/ServiceNow-Codefresh Integration_1.2.0.xml] installed on the instance

### Documentation

Product Documentation: https://docs.servicenow.com/

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | DEFAULT | TYPE | REQUIRED | VALUES | DESCRIPTION |
| :----------------------------| :----------: | :---------| :---: |----------|---------------------------------------------------------------------------------------------------------------------------------|
| SN_INSTANCE | N/A | URL string | yes | | the instance url as https://myinstance.service-now.com |
| SN_USER | N/A | string | yes | | userid to connect to the instance |
| SN_PASSWORD | N/A | string | yes | | password to connect to the instance |
| CR_ACTION | createCR | string | no | createCR, closeCR, updateCR | the operation to execute |
| CR_CONFLICT_POLICY | ignore | string | no | ignore, wait, reject | What do when a schedule conflict arises |
| CR_DATA | N/A | JSON string | no | JSON block | the JSON block to pass when opening, updating or closing a CR |
| CR_SYSID | N/A | string | no | uuid | the sysid of the CR record as returned by the createCR action. USed to update or close a CR |
| CR_CLOSE_CODE | successful | string | no | sucessful or any value accepted by the close_code field |
| CR_CLOSE_NOTES | N/A | string | no | Any string accepted for the close_notes field |


### codefresh.yml

Codefresh build step to execute AWS CDK commands

```yaml
version: "1.0"

stages:
  - clone
  - build
  - deploy
  - test
  - post

steps:

  build:
    title: "Building my Application"
    image: "codefresh/cli"
    stage: "build"
    commands:
      - echo "Building App"
      
  calculateDate:
     title: "Calculate date for the palnned schedule"
    image: ubuntu:latest
    stage: deploy
    commands:
      - |
        START_DATE=`date -u '+%Y-%m-%d %H:%M:%S'`
        END_DATE=`date -u -d '+1 hour' '+%Y-%m-%d %H:%M:%S'`
        echo START_DATE=\"$START_DATE\" >> ${{CF_VOLUME_PATH}}/env_vars_to_export
        echo  END_DATE=\"$END_DATE\" >> ${{CF_VOLUME_PATH}}/env_vars_to_export
        
  createCR:
    type: service-now
    title: Create Service Now Change Request
    stage: deploy
    arguments:
      CR_ACTION: createCR
      SN_USER: admin
      SN_PASSWORD: '${{SN_PASSWORD}}'
      SN_INSTANCE: https://XXXXXX.service-now.com
      TOKEN: ${{CF_TOKEN}}
      CR_CONFLICT_POLICY: reject
      CR_DATA: >-
        {"short_description": "Globex deployment to Visa QA", 
        "description": "Change for build ${{CF_BUILD_ID}}.\nThis change was created by the Codefresh plugin", 
        "justification": "I do not need a justification\nMy app is awesome",
        "cmdb_ci":"tomcat",
        "start_date":${{START_DATE}},
        "end_date":${{END_DATE}}
        }

  wait:
    stage: deploy
    type: pending-approval
    timeout:
      duration: 2
      finalState: denied    
    
  modifyCR:
    stage: deploy
    title: "Modify the implementation plan"
    type: service-now
    fail_fast: false
    arguments:
      CR_ACTION: updateCR
      CR_SYSID: ${{CR_SYSID}}
      SN_USER: admin
      SN_PASSWORD: '${{SN_PASSWORD}}'
      SN_INSTANCE: https://XXXXXX.service-now.com
      CR_DATA: '{"implementation_plan":"The implementation has been approved."}' 
      
  deploy:
    title: "Deploying my Application"
    image: "codefresh/cli"
    stage: "deploy"
    commands:
      - echo "Deploying App"
      - sleep 5

  test:
    title: "Testing my Application"
    image: "codefresh/cli"
    stage: "test"
    commands:
      - echo "Testing App"
      - sleep 10
      
  modifyTestPlan:
    stage: test
    title: "Modify the test plan"
    type: service-now
    fail_fast: false
    arguments:
      CR_ACTION: updateCR
      CR_SYSID: ${{CR_SYSID}}
      SN_USER: admin
      SN_PASSWORD: '${{SN_PASSWORD}}'
      SN_INSTANCE: https://XXXXXX.service-now.com
      CR_DATA: '{"test_plan":"The testing suit has passed."}'
 
  closeCR:
    type: service-now
    title: Close Service Now Change Request
    stage: post
    arguments:
      CR_ACTION: closeCR
      CR_SYSID: ${{CR_SYSID}}
      SN_USER: admin
      SN_PASSWORD: '${{SN_PASSWORD}}'
      SN_INSTANCE: https://XXXXXX.service-now.com
      CR_CLOSE_CODE: "successful"
      CR_CLOSE_NOTES: "Closed automatically by Codefresh build ${{CF_BUILD_ID}}"
      CR_DATA: '{"work_notes":"this is a message for the work notes"}'

```
