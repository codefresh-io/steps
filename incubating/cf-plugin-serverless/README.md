# Codefresh Serverless Plugin

Use Codefresh [Serverless](https://serverless.com/framework/) plugin to deploy a Serverless service to specified serverless provider.

## Usage

Use [Codefresh Serverless Framework Plugin](https://github.com/codefresh-io/cf-plugin-serverless) to deploy Serverless service (functions and resources) to the Amazon AWS cloud.

```yaml
---
version: '1.0'

steps:

  setup:
    image: alpine:3.7
    title: generate AWS shared credentials file
    commands:
      - mkdir -p .aws
      - echo -n $AWS_CREDENTIALS_FILE | base64 -d > ${PWD}/.aws/credentials
      - cf_export AWS_SHARED_CREDENTIALS_FILE=${PWD}/.aws/credentials

  package:
    image: codefresh/serverless:1.28
    title: package serverless service
    working_directory: ${{main_clone}}/examples/aws-node-simple-http-endpoint
    commands:
      - serverless package --stage ${AWS_STAGE} --region ${AWS_REGION} --package ${PACKAGE}

  deploy:
    image: codefresh/serverless:1.28
    title: deploy to AWS with serverless framework
    working_directory: ${{main_clone}}/examples/aws-node-simple-http-endpoint
    commands:
      - serverless deploy --conceal --verbose --stage ${AWS_STAGE} --region ${AWS_REGION} --aws-profile ${AWS_PROFILE} --package ${PACKAGE}
```

## Environment Variables

| Variables                   | Provider |  Description                            |
|-----------------------------|----------|-----------------------------------------|
| PACKAGE                     | All      | Serverless Framework package folder     |
|                             |          |                                         |
| AWS_CREDENTIALS_FILE        | AWS      | `Base64` encoded AWS `credentials` file |
| AWS_SHARED_CREDENTIALS_FILE | AWS      | path to shared AWS `credentials` file   |
| AWS_REGION                  | AWS      | AWS region                              |
| AWS_PROFILE                 | AWS      | AWS credentials profile                 |
| AWS_STAGE                   | AWS      | AWS API Gateway stage                   |
