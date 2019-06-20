# Codefresh Anchore Plugin

Anchore is a service that analyzes Docker images and generates a detailed manifest of the image, a virtual ‘bill of materials’ that includes official operating system packages, unofficial packages, configuration files, and language modules and artifacts. Anchore policies can they be defined to govern security vulnerabilities, package whitelists and blacklists, configuration file contents, presence of credentials in image, manifest changes, exposed ports or any user defined checks. These policies can be deployed site wide or customized for specific images or categories of applications.

For more information view the github repo here: https://github.com/anchore/anchore-engine

## Prerequisites

- Codefresh subscription
- Running Anchore Engine service

### Reference

- Example `codefresh.yml`: https://raw.githubusercontent.com/valancej/plugins/master/plugins/anchore/codefresh.yml
- Github repo containing Dockerfile: https://github.com/valancej/node_critical_fail
- Anchore Documentation: https://anchore.freshdesk.com/support/home
- Anchore CLI Image: https://hub.docker.com/r/anchore/engine-cli/

## Example

In this example, we will scan an image built by Codefresh. Depending on the result of the Anchore policy evaluation, we will choose to push the image to Dockerhub or not. 

### Setup

The example setup is described below. 

### Environment Variables

These environment variables can be set within Codefresh pipeline configuration.

Name|Required|Description
---|---|---
ANCHORE_CLI_URL|Yes|The address of the Anchore server
ANCHORE_CLI_USER|Yes|Anchore account name
ANCHORE_CLI_PASS|Yes|Anchore account password
ANCHORE_FAIL_ON_POLICY|No|Fail build if policy evaluation fails
QA_IMAGE|No|Image built and scanned
dockerhubUsername|No|Dockerhub account name
dockerhubPassword|No|Dockerhub account password

### Codefresh.yml

```yaml
version: '1.0'
steps:
  MyDockerImage:
    title: Building Docker Image
    type: build
    image_name: ${{QA_IMAGE}}
    working_directory: ./
    tag: latest
    dockerfile: Dockerfile
    metadata:
      set:
      	- QA: Pending Anchore scan before push to Dockerhub..
  ScanMyImage:
    title: Scanning Docker Image
    image: anchore/engine-cli:latest
    commands:
      - echo "Scanning image with Anchore"
      - anchore-cli image add ${{QA_IMAGE}}
      - echo "Waiting for analysis to complete"
      - anchore-cli image wait ${{QA_IMAGE}}
      - echo "Analysis complete"
      - if [ "${{ANCHORE_FAIL_ON_POLICY}}" == "true" ] ; then anchore-cli evaluate check ${{QA_IMAGE}}; fi
  PushImage:
    title: Pushing Docker Image
    description: Pushing Docker Image to Dockerhub...
    type: push
    candidate: '${{MyDockerImage}}'
    image_name: jvalance/node_critical_fail
    tag: latest
    registry: docker.io
    credentials:
      username: '${{dockerhubUsername}}'
      password: '${{dockerhubPassword}}'
```