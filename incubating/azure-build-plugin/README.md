# Docker build using Azure ACR


## Run locally
`docker run -it codefresh/cf-azure-builder`
```
NAME:
   cf-azure-builder

DESCRIPTION:
   Build 

## Mandatory Parameters:

    AUTH            - Authentication mode. By default it is Azure user credentials. 
                      (Use 'service-princpal' value in case you want to authenticate using service principal)
    USER            - Azure user name (not needed if authentication mode is service-principal)
    IMAGE           - Image name
    TAG             - Tag name
    ACR_NAME        - ACR registry name
    APP_ID          - Azure service principal application id (only needed if authentication mode is service-principal)
    PASSWORD        - Azure user\service principal password
    TENANT          - Azure ad tenant id (only needed if authentication mode is service-principal)
    DOCKERFILE_PATH - Dockerfile path (default - working_dir/Dockerfile)
    
## Output Variables

    AZURE_IMAGE     - Azure image full name in ACR that can be used in later step

## Usage Example:

## service principal

version: '1.0'
steps:
  cf-az-build:
    image: codefreshplugins/cf-azure-builder
    environment:
      - AUTH=service-principal
      - IMAGE=<image name>
      - TAG=<tag name>
      - ACR_NAME=<acr registry name>
      - APP_ID=<azure service principal application id>
      - PASSWORD=<azure service principal password>
      - TENANT=<azure ad tenant id>
      - DOCKERFILE_PATH=<dockerfile path>

## user credentials

image: 'codefresh/cf-azure-builder'
environment:
  - IMAGE=<image name>
  - TAG=<tag name>
  - ACR_NAME=<acr registry name>
  - USER=<azure user name>
  - PASSWORD=<azure user password>
