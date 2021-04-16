# AWS CDK wrapper

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

### Documentation

Getting started with AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | Default value | Type | Required | Values | Description |
| :----------------------------| :----------: | :---------| :---: |----------|---------------------------------------------------------------------------------------------------------------------------------|
| action | deploy | string | yes | deploy, destroy, synth<br/>To come: bootstrap, diff, list, freestyle |The CDK operation to execute |
| cdk_version | 1.98.0 | string | no | 1.90.0, 1.94.1, 1.98.0 | Version of the CDK used in the image |
| language | TypeScript | string | yes | TypeScript, Python | The language for the application |
| project_dir | . | string | no | | the folder where the CDK app is located |
| verbose | true | boolean | no | true, false | Add the --verbose flag to the command if true |
| stacks | | string | no | a comma-separated list of stacks|
| AWS_ACCESS_KEY_ID | | string | no | Amazon access key|
| AWS_SECRET_ACCESS_KEY | | string | no | Amazon secret key.<br/>Don't forget to encrypt it|
| AWS_DEFAULT_REGION | us-east-1 | string | no | Amazon region|



### codefresh.yml

Codefresh build step to execute AWS CDK commands

```yaml
version: "1.0"

stages:
  - clone
  - build
  - synth
  - deploy
  - destroy

steps:
  gitClone:
    title: Cloning Sample Project Repository
    type: git-clone
    stage: clone
    arguments:
      repo: codefresh-io/aws-cdk-samples
      revision: main

  projectBuild:
    stage: build
    title: Building the lambda CDK project for TypeScript
    type: freestyle
    working_directory: ${{gitClone}}/lambda-cron
    image: node
    commands:
      - npm install -g aws-cdk
      - npm install
      - npm run build

  deploy:
    stage: deploy
    title: Deploy the Typescript app
    type: aws-cdk
    registry: docker-lr
    working_directory: ${{gitClone}}/lambda-cron
    arguments:
      action: deploy
      language: typescript
      #verbose: true
      #cdk_version: 1.98.0
      AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
      AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
      AWS_SESSION_TOKEN: ${{AWS_SESSION_TOKEN}}

  wait-approval:
    title: "Wait for approval before destruction"
    stage: destroy
    type: "pending-approval"
    timeout:
      duration: 1
      finalState: denied

  destroy:
    title: "Destroying the TypeScript lambda CDK project"
    stage: destroy
    type: aws-cdk
    working_directory: ${{gitClone}}/lambda-cron
    arguments:
      action: destroy
      cmd_ps: --force
      verbose: false
      language: typescript
      AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
      AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
      AWS_SESSION_TOKEN: ${{AWS_SESSION_TOKEN}}

```
