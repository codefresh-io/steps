# cfstep-prisma-cloud

Scan Docker images using Prisma Cloud.

Images must be pushed to registry that is connected to Prisma Cloud.

As an alternative a use can use the Docker image built and run it as container in Codefresh installing twistcli and initiating the scan from that container.

```
version: 1.0
stages:
  - clone
  - build
  - scan
  - push

steps:
  clone:
    title: Cloning repository...
    type: git-clone
    repo: ${{CF_REPO_OWNER}}/${{CF_REPO_NAME}}
    revision: ${{CF_REVISION}}
    stage: clone

  build:
    title: Building Docker image..
    type: build
    image_name: ${{CF_REPO_NAME}}
    working_directory: ${{clone}}
    tag: ${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}
    dockerfile: Dockerfile
    stage: build

  push:
    title: Pushing Docker image...
    type: push
    candidate: ${{build}}
    registry: gcr
    tag: ${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}
    stage: push

  scan:
    title: Scanning Docker image
    image: ${{build}}
    commands:
      - echo "Installing curl... <Optional>"
      - apk add curl
      - echo "Downloading twistcli... <Required>"
      - curl -k -u "${{PC_USERNAME}}:${{PC_PASSWORD}}" --output ./twistcli "${{PC_PROTOCOL}}://${{PC_HOSTNAME}}:${{PC_PORT}}/api/v1/util/twistcli"
      - chmod +x ./twistcli
      - echo "Scanning codefresh-sa/${{CF_REPO_NAME}}"
      - ./twistcli images scan --ci --details -address "${{PC_PROTOCOL}}://${{PC_HOSTNAME}}:${{PC_PORT}}" -u "${{PC_USERNAME}}" -p "${{PC_PASSWORD}}" --containerized  "codefresh-sa/${{CF_REPO_NAME}}:${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}" --custom-labels Build="${{CF_BUILD_URL}}"
    stage: scan
    on_finish: 
      annotations:
        set:
          - entity_id: ${{CF_BUILD_ID}}
            entity_type: build
            annotations:
            - prisma_cloud_report: ${{PC_PROTOCOL}}://${{PC_HOSTNAME}}:${{PC_PORT}}/#!/monitor/vulnerabilities/images/registries?search=${{CF_REPO_NAME}}:${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}
          - entity_id: ${{build.imageId}}
            entity_type: image
            annotations:
            - prisma_cloud_report: ${{PC_PROTOCOL}}://${{PC_HOSTNAME}}:${{PC_PORT}}/#!/monitor/vulnerabilities/images/registries?search=${{CF_REPO_NAME}}:${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}
```