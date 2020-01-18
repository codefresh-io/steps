## Overview

The Codefresh step scans the list of docker images and sends the report to a Slack webhook URL.

## Arguments
- **GITHUB_TOKEN**. To avoid the error because the "GitHub API limit is exceeded".
- **SLACK_INCOMING_URL**. Slack webhook URL to send the report to it.
- **IMAGES_FILE**. Path to the file with list of images to scan.
- **IMAGES_LIST**. List of images to scan. Can be used in conjunction with **IMAGES_FILE**, the resulting list of images is the sum of both.
- **TRIVY_IGNORE_FILE**. Path to the file with list of vulnerabilities to ignore.
- **TRIVY_IGNORE_LIST**. List of vulnerabilities to ingore. Can be used in conjunction with **TRIVY_IGNORE_FILE**.
- **TRIVY_USERNAME**. DockerHub username. Required in case of private registry. 
- **TRIVY_PASSWORD**. DockerHub password. Required in case of private registry. 
- **SKIP_EMPTY**. Do not attach to the report message images with empty vulnerabilities list.

## Example
```yaml
version: '1.0'

steps:
  Clone:
    type: git-clone
    arguments:
      repo: '${{CF_REPO_OWNER}}/${{CF_REPO_NAME}}'
      git: codefresh
      revision: '${{CF_REVISION}}'

  export_vars:
    title: export env vars
    image: codefresh/cli
    commands:
      - cf_export GITHUB_TOKEN=$(codefresh get contexts <MY GITHUB CONTEXT> --type git.github -o json --decrypt | jq -r .spec.data.auth.password )

  scan:
    title: Scan images
    type: codefresh-plugins/trivy-scan
    arguments:
      SLACK_INCOMING_URL: http://my.webhook.url
      GITHUB_TOKEN: '${{GITHUB_TOKEN}}'
      IMAGES_FILE: ./${{CF_REPO_NAME}}/images.list
      IMAGES_LIST:
        - docker:18.09.5-dind
        - alpine:latest
      TRIVY_IGNORE_FILE: ./${{CF_REPO_NAME}}/.trivyignore
      TRIVY_IGNORE_LIST:
        - CVE-2019-1551
```

