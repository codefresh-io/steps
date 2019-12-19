# Codefresh Anchore Plugin

Anchore is a service that analyzes Docker images and generates a detailed manifest of the image, a virtual ‘bill of materials’ that includes official operating system packages, unofficial packages, configuration files, and language modules and artifacts. Anchore policies can be defined to govern security vulnerabilities, package whitelists and blacklists, configuration file contents, presence of credentials in image, manifest changes, exposed ports or any user defined checks. These policies can be deployed site wide or customized for specific images or categories of applications.

For more information view the github repo here: https://github.com/anchore/anchore-engine

## Prerequisites

- Codefresh subscription
- Running Anchore Engine service

### Steps arguments

Name|Required|Description
---|---|---
ANCHORE_CLI_URL|Yes|The address of the Anchore server
ANCHORE_CLI_USER|Yes|Anchore account name
ANCHORE_CLI_PASS|Yes|Anchore account password
ANCHORE_FAIL_ON_POLICY|No|Fail build if policy evaluation fails
ANCHORE_CLI_IMAGE|No|Image to scan

### Codefresh.yml

```yaml
version: '1.0'
steps:
  ScanMyImage:
    title: Scanning Docker Image
    type: anchore
    arguments:
      ANCHORE_CLI_URL: http://<URL_TO_ANCHORE_ENGINE>
      ANCHORE_CLI_USER: admin
      ANCHORE_CLI_PASS: foobar
      ANCHORE_CLI_IMAGE: alpine:latest
      ANCHORE_FAIL_ON_POLICY: "false"
```
