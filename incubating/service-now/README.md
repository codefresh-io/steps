# ServiceNow integration

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

### Documentation

Product Documentation: https://docs.servicenow.com/

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | DEFAULT | TYPE | REQUIRED | VALUES | DESCRIPTION |
| :----------------------------| :----------: | :---------| :---: |----------|---------------------------------------------------------------------------------------------------------------------------------|
| action | createCR | string | no | createCR | the operation to execute |

### codefresh.yml

Codefresh build step to execute AWS CDK commands

```yaml
version: '1.0'
stages:
  - "clone"
  - "build"
  - "deploy"

steps:
  gitClone:
    title: Cloning Project Repo
    type: git-clone
    stage: clone
    arguments:
      repo: ${{CF_REPO_OWNER}}/${{CF_REPO_NAME}}
      revision: ${{CF_REVISION}}

  projectBuild:
    title: Building your application
    stage: build
    image: alpine
    working_directory: ${{gitClone}}/${{CF_REPO_NAME}}
    commands:
      - echo "Building app..."

  CreateChangeRequest:
    title: Deploy the app
    type: service-now
    stage: deploy
    arguments:
      action: createCR
      title: "Change Request for deployment of myAwesomeApp"
      description: "Approval for deployment of myAwesomeApp in QA. Test results indicate ${{TEST_SUCCESS_RATE}}%."
      SN_INSTANCE: https://instance1.service-now.com
      SN_USER: ${{SN_USER}}
      SN_PASSWORD: ${{SN_PASSWORD}}

  approval:
    title: Approval will be done automatically from ServiceNow
    stage: deploy
    type: pending-approval
    working_directory: ${{gitClone}}/cdk/lambda-cron
    timeout:
      duration: 24
      finalState: denied

```
