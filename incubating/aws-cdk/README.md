# AWS CDK wrapper

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

### Documentation

Getting started with AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | DEFAULT | TYPE | REQUIRED | VALUES | DESCRIPTION |
| :----------------------------| :----------: | :---------| :---: |----------|---------------------------------------------------------------------------------------------------------------------------------|
| action | deploy | string | yes | deploy, destroy<br/>To come: synth, bootstrap, diff, list, freestyle |The CDK operation to execute |
| project_dir | . | string | no | | the folder where the CDK app is located |
| language | TypeScript | string | yes | TypeScript, Python | The language for the application |
| verbose | true | boolean | no | true, false | Add the --verbose flag to the command if true |
| cdk_version | 1.94.1 | string | no | 1.90.0, 1.94.1 | Version of the CDK used in the image |
| AWS_ACCESS_KEY_ID | | string | no | Amazon access key|
| AWS_SECRET_ACCESS_KEY | | string | no | Amazon secret key.<br/>Don't forget to encrypt it|
| AWS_DEFAULT_REGION | us-east-1 | string | no | Amazon region|
| stacks | | string | no | a comma-separated list of stacks|


### codefresh.yml

Codefresh build step to execute AWS CDK commands

```yaml
version: '1.0'
stages:
  - "clone"
  - "build"
  - "test"

steps:
  gitClone:
    title: Cloning Project Repo
    type: git-clone
    stage: clone
    arguments:
      repo: ${{CF_REPO_OWNER}}/${{CF_REPO_NAME}}
      git: github
      revision: ${{CF_REVISION}}

  projectBuild:
    title: Building the lambda CDK project
    stage: build
    working_directory: ${{gitClone}}/cdk/lambda-cron
    arguments:
      image: node
      commands:
        - npm install -g aws-cdk
        - npm install
        - npm run build

  AwsCDKDeploy:
    title: Deploy the app
    type: cf-support/aws-cdk
    stage: test
    working_directory: ${{gitClone}}/cdk/lambda-cron
    arguments:
      action: deploy
      language: TypeScript
      verbose: true
      cdk_version: 1.94.1
      AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
      AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
      AWS_SESSION_TOKEN: ${{AWS_SESSION_TOKEN}}

  projectDestroy:
    title: Destroying the lambda CDK project
    stage: test
    type: cf-support/aws-cdk
    working_directory: ${{gitClone}}/cdk/lambda-cron
    arguments:
      action: destroy
      cmd_ps: --force
      verbose: true
      cdk_version: 1.94.1
      AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
      AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
      AWS_SESSION_TOKEN: ${{AWS_SESSION_TOKEN}}


```
