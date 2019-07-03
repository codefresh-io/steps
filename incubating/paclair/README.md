# cfstep-paclair [![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/codefresh-inc/codefresh-contrib%2Fcfstep-paclair%2Fcfstep-paclair?branch=master&type=cf-1)]( https://g.codefresh.io/repositories/codefresh-contrib/cfstep-paclair/builds?filter=trigger:build;branch:master;service:5bbe7af8a3686e081e4e1b91~cfstep-paclair)

Custom Docker image to support clair image scanning from Codefresh pipeline

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

Running Clair Instance -
Helm Chart is available to install here: https://github.com/coreos/clair/tree/master/contrib/helm

### Documentation:

paclair: https://github.com/yebinama/paclair

### Tested Registries

Codefresh Registry - No special setup required.

Username is your Codefresh Username and Docker Registry keys can be created here https://g.codefresh.io/user/settings

ECR - Requires AWS CLI credentials with access to ECR.
`REGISTRY=ecr` will find the proper ECR registry using your credentials and image.

AWS CLI Credentials required for ECR:
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

| ENVIRONMENT VARIABLE |
| --------------------- |
| AWS_ACCESS_KEY_ID |
| AWS_DEFAULT_REGION |
| AWS_SECRET_ACCESS_KEY |

Registries with Basic auth and Token based auth should work.

### Full List of Options

To use an ENVIRONMENT VARIABLE you need to add the variables to your Codefresh Pipeline and also to your codefresh.yml.

Example `codefresh.yml` build is below with required ENVIRONMENT VARIABLES in place.

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| API_PREFIX | null | string | No | Prefix for API to Docker Registry |
| CF_ACCOUNT | Codefresh Account Name | string | No | Codefresh Account Name (Skipped for ECR) |
| CLAIR_URL | null | string | Yes | https://clair.domain.com:6060 |
| IMAGE | null | string | Yes | Docker Image Name |
| PROTOCOL | https | string | No | Docker Registry Protocol |
| REGISTRY | r.cfcr.io | string | No | For ECR use `ecr` else use domain name for Docker Registry |
| REGISTRY_PASSWORD | null | string | Yes | Docker Registry Password |
| REGISTRY_USERNAME | null | string | Yes | Docker Registry Username |
| SEVERITY_THRESHOLD | null | string | No | critical, high, medium, low, negligible, unknown |
| TOKEN | null | string | No | Docker Registry Auth Token |
| TOKEN_TYPE | Bearer | string | No | Docker Registry Auth Token Type |
| TOKEN_URL | null | string | No | Docker Registry Auth Token URL |
| TAG | null | string | Yes | Docker Image Tag |

### SEVERITY_THRESHOLD

If variable is set step will check that the threshold is not met or exceeded.  

For example, high would fail your build if you had high or critical vulnerabilties on your Docker image.

### codefresh.yml

Codefresh Build Step to execute Clair scan.
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
    tag: '${{CF_BRANCH_TAG_NORMALIZED}}'
  CheckClair:
    image: codefreshplugins/cfstep-paclair:3.1.0
    environment:
      - IMAGE=example-voting-app/worker # Replace with your Docker image name
      - TAG=${{CF_BRANCH_TAG_NORMALIZED}}
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
  ArchiveReport:
    image: mesosphere/aws-cli
    commands:
      - aws s3 cp ./reports/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html s3://${{S3_BUCKETNAME}}/${{CF_BUILD_ID}}/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html --acl public-read
    on_success:
     metadata:
        set:
          - ${{BuildingDockerImage.imageId}}:
              - CLAIR_REPORT: "https://s3.amazonaws.com/${{S3_BUCKETNAME}}/${{CF_BUILD_ID}}/clair-scan-example-voting-app-worker-${{CF_BRANCH_TAG_NORMALIZED}}.html"
```

The HTML report is stored in `./reports/clair-scan-{image name}-{image tag}.html`
Any `/` characters in `{image name}` are replaced with `-`

Optional Storage Step Variables for AWS S3:

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID | null | string | No | AWS Access Key of S3 Bucket |
| AWS_DEFAULT_REGION | null | string | Yes | AWS Region of S3 Bucket |
| AWS_SECRET_ACCESS_KEY | null | string | Yes | AWS Secret Key of S3 Bucket |
| S3_BUCKETNAME | null | string | Yes | Name of S3 Bucket to Store Reports |

### Notes

Not yet supporting manual Cert validation.  Coming soon along with tests.
