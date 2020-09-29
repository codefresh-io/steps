# yaml-pop-it

Custom step that will create and populate configMap and secrets manifests for a deployment.

3 supported sources for variables.

1. Variable POPs
1. Codefresh Shared Config
1. Google Secret Manager

### Prerequisites:

Deployment Manifest

### Documentation:

The step's arguments suppport variable interpolation in two ways.

1. Inplace interpolation - An argument like `SERVICE_NAME: myservice` will replace any instance of `${SERVICE_NAME}` or `${SERVICE.NAME}` and is case-insensitive.
1. POPs - An argument like `POP_CONFIG_EXAMPLE_VAR: MYVALUE` will create a new configMap value of `EXAMPLE_VAR: MYVALUE` and `POP_SECRET_EXAMPLE_SECRET: MYVALUE` will create a new secret value of `EXAMPLE_SECRET: MYVALUE` with `MYVALUE` being base64encoded before being pushed into secret manifest.

The step will automatically parse from the Deployment Manifest the name of the configMap and secret from the volumes of the container.

``` console
      volumes:
        - name: configs-${service.name}
          configMap:
            name: ${TEST_API_CONFIG}
        - name: secrets-${service.name}
          secret:
            secretName: ${TEST_API_SECRET}
```

It then will search Codefresh Shared Configurations for Shared Configs matching `TEST_API_CONFIG` and Shared Secrets matching `TEST_API_SECRET`.

If you provide `GOOGLE_PROJECT_NAME` argument and import your SA JSON to the pipeline then the step will look up secrets from Google Secret Manager by Label.  The default Label Name is `secret-name` and the default value is the secretName you provided in your volume declaration above but conformed to lower-case and hyphen characters instead of underscores to support the Google Labeling convention.

### Full List of Arguments

| Arguments | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| DEPLOYMENT_FILE | null | path | Yes | Path to Deployment Manifest |
| GOOGLE_APPLICATION_CREDENTIALS | ./sa.json | path | No | Path to sa.json file |
| GOOGLE_LABEL_KEY | secret-name | string | No | Label Key for Secret |
| GOOGLE_LABEL_VALUE | Pulled from Deployment Manifest | string | No | Label Value for Secret |
| GOOGLE_PROJECT_NAME | null | string | No | Google Project Name |
| SERVICE_NAME | null | string | Yes | Name of the Kubernetes Service |
| TEMPLATES_DIRECTORY | /templates | path | No | Directory containing templates for configMap and secrets Kubernetes Manifests |
| WORKING_DIRECTORY | /codefresh/volume | path | No | Directory to place interpolated/created Kubernetes Manifests |

### codefresh.yml

Codefresh Build Step to execute Clair scan.
All `${{var}}` variables must be put into Codefresh Build Parameters
codefresh.yml

``` console
# More examples of Codefresh YAML can be found at
# https://codefresh.io/docs/docs/yaml-examples/examples/

version: "1.0"
# Stages can help you organize your steps in stages
stages:
  - clone
  - "prepare credentials"
  - "prepare deployment"
  - deploy

steps:
  clone:
    title: Cloning repository...
    type: git-clone
    repo: ${{CF_REPO_OWNER}}/${{CF_REPO_NAME}}
    revision: ${{CF_BRANCH}}
    git: github
    stage: clone
    
  prepare_credentials:
    title: Writing sa.json...
    image: alpine
    commands:
      - echo "${{BASE64_SA_JSON}}" | base64 -d > sa.json
    stage: "prepare credentials"

  rev_pipeline:
    title: Revving build number...
    type: bump-build-number
    stage: "prepare deployment"

  prepare_deployment:
    title: Preparing deployment manifests...
    type: codefreshdemo/yaml-pop-it
    arguments:
      APP_NAME: ${{APP_NAME}}
      CF_BUILD_NUMBER: ${{CF_BUILD_NUMBER}}
      DEPLOYMENT_FILE: ${{CF_VOLUME_PATH}}/${{CF_REPO_NAME}}/deployment.yaml
      DOCKER_IMAGE_NAME: ${{DOCKER_IMAGE_NAME}}
      GOOGLE_APPLICATION_CREDENTIALS: sa.json
      GOOGLE_PROJECT_NAME: codefresh-sa
      SERVICE_NAME: test-service
      WORKING_DIRECTORY: ${{CF_VOLUME_PATH}}/${{CF_REPO_NAME}}
    stage: "prepare deployment"
  
  k8s_deploy:
    title: Deploying Manifests to Kubernetes...
    image: codefresh/cf-deploy-kubernetes:master
    working_directory: ${{clone}}
    commands:
      - /cf-deploy-kubernetes ${{SERVICE_NAME}}-configmap-${{CF_BUILD_NUMBER}}.yaml
      - /cf-deploy-kubernetes ${{SERVICE_NAME}}-secrets-${{CF_BUILD_NUMBER}}.yaml
      - /cf-deploy-kubernetes ${{SERVICE_NAME}}-deployment-${{CF_BUILD_NUMBER}}.yaml  
    environment:
      - KUBECONTEXT=${{KUBE_CONTEXT}}
      - KUBERNETES_NAMESPACE=${{KUBE_NAMESPACE}}
    stage: deploy
```
