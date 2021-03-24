# AWS CDK wrapper

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

### Documentation

Getting started with AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | DEFAULT | TYPE | REQUIRED | VALUES | DESCRIPTION |
|----------------------------|----------|---------|----------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| action | | string | yes | synth, bootstrap, deploy, diff, list, destroy, freestyle |The CDK operation to execute |
| project_dir | . | string | no | | the folder where the CDK app is located |
| language | TypeScript | string | yes | TypeScript, python | The language for the application |



### codefresh.yml

Codefresh build step to execute AWS CDK commands

```yaml
version: '1.0'
stages:
  - cdk

steps:
  cdk-synth:
    TBD  

```

### Using as freestyle step

See documentation here: [https://codefresh.io/docs/docs/new-helm/using-helm-in-codefresh-pipeline/](https://codefresh.io/docs/docs/new-helm/using-helm-in-codefresh-pipeline/)
