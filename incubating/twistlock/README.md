# Twistlock CLI

Docker image which invokes security script using Twistlock CLI

### Prerequisites:

Codefresh Subscription (Dedicated Infrastructure/Hybrid) - https://codefresh.io/

Twistlock Subscription - https://www.twistlock.com/

### Documentation:

Twistlock CLI: https://twistlock.desk.com/customer/en/portal/articles/2879128-scan-images-with-twistcli

## Local Usage

``` sh
docker run --volume /var/run/docker.sock:/var/run/docker.sock sctechtech/docker-twistcli:latest twistcli images scan <Docker Image Name or ID> --address <Twistlock Console Address> --user <Twistlock Console User> --password '<Twistlock Console Password>' --include-files --include-package-files --details
```

## Script Library

### twistlock-cli.py for Codefresh

Executes TwistCLI to scan Docker image given.

### TLS is partially supported for uploading contents to your Twist Console but certification is skipped when downloading the Report URL from the server which takes place later.

Extracting Cert:

``` sh
openssl s_client -connect <URL>:<PORT>
```

Copy out the lines beginning with and including `-----BEGIN CERTIFICATE-----` up to and including `-----END CERTIFICATE-----`

You can past that into a Codefresh variable `TLSCACERT` without reformatting.
Script will take care of that.

The add the entry below to your `environment:` array in the `TwistlockScanImage`

`- VULNERABILITY_THRESHOLD=${{VULNERABILITY_THRESHOLD}}`

### Full List of Options

To use an ENVIRONMENT VARIABLE you need to add the variables to your Codefresh Pipeline and also to your codefresh.yaml.

Example `codefresh.yml` build is below with required ENVIRONMENT VARIABLES in place.

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| CODEFRESH_CLI_KEY | null | string | Yes | https://g.codefresh.io/account/tokens |
| CONSOLE_HOSTNAME | null | string | Yes | hostname/ip |
| CONSOLE_PORT | null | string | Yes | port |
| CONSOLE_USERNAME | null | string | Yes | username |
| CONSOLE_PASSWORD | null | string | Yes | password |
| TLSCACERT | null | string | No | CA Cert if provided TLS will be used |
| HASH | [ sha1 ] | string | No | [ md5, sha1, sha256 ] hashing algorithm |
| DETAILS | null | boolean | No | prints an itemized list of each vulnerability found by the scanner |
| INCLUDE_PACKAGE_FILES | null | boolean | No | List all packages in the image. |
| ONLY_FIXED | null | boolean | No | reports just the vulnerabilites that have fixes available |
| COMPLIANCE_THRESHOLD | null | string | No | [ low, medium, high ] sets the the minimal severity compliance issue that returns a fail exit code |
| VULNERABILITY_THRESHOLD | null | string | No | [ low, medium, high, critical ] sets the minimal severity vulnerability that returns a fail exit code |

### codefresh.yml

Codefresh Build Step to execute Twistlock scan.
All `${{var}}` variables must be put into Codefresh Build Parameters
codefresh.yml
``` console
version: '1.0'
steps:
  BuildingDockerImage:
    title: Building Docker Image
    type: build
    image_name: codefresh/demochat # Replace with your Docker image name
    working_directory: ./
    dockerfile: Dockerfile
    tag: '${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}}'
  TwistlockScanImage:
    type: composition
    composition:
      version: '2'
      services:
        targetimage:
          image: ${{BuildingDockerImage}} # Must be the Docker build step name
          command: sh -c "exit 0"
          labels:
            build.image.id: ${{CF_BUILD_ID}} # Provides a lookup for the composition
    composition_candidates:
      scan_service:
        image: sctechdev/docker-twistcli:latest # Recommend replacing with current Twistlock Console version
        environment: # Add only the Environment Variables you need
          - CODEFRESH_CLI_KEY=${{CODEFRESH_CLI_KEY}} # Required
          - CONSOLE_HOSTNAME=${{CONSOLE_HOSTNAME}} # Required
          - CONSOLE_PORT=${{CONSOLE_PORT}} # Required
          - CONSOLE_USERNAME=${{CONSOLE_USERNAME}} # Required
          - CONSOLE_PASSWORD=${{CONSOLE_PASSWORD}} # Required
          - COMPLIANCE_THRESHOLD=${{COMPLIANCE_THRESHOLD}} # Optional Example
          - VULNERABILITY_THRESHOLD=${{VULNERABILITY_THRESHOLD}} # Optional Example
        command: python /twistlock-cli.py "docker inspect $$(docker inspect $$(docker ps -aqf label=build.image.id=${{CF_BUILD_ID}}) -f {{.Config.Image}}) -f {{.Id}} | sed 's/sha256://g'"
        depends_on:
          - targetimage
        volumes: # Volumes required to run DIND
          - /var/run/docker.sock:/var/run/docker.sock
          - /var/lib/docker:/var/lib/docker
    add_flow_volume_to_composition: true
    on_success: # Execute only once the step succeeded
      metadata: # Declare the metadata attribute
        set: # Specify the set operation
          - ${{BuildingDockerImage.imageId}}: # Select any number of target images
            - SECURITY_SCAN: true

    on_fail: # Execute only once the step failed
      metadata: # Declare the metadata attribute
        set: # Specify the set operation
          - ${{BuildingDockerImage.imageId}}: # Select any number of target images
            - SECURITY_SCAN: false
```