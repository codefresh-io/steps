
# cf-ecs-deploy
Deployment to Amazon ECS Service

### Prerequiests
- Configured ECS Cluster with at least one running instance.
- Configured ECS Service and task definition with an image being deployed.
  See http://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html

- AWS Credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) with following priviledges:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1479146904000",
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTasks",
        "ecs:ListClusters",
        "ecs:ListServices",
        "ecs:ListTasks",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
```

### Deployment with Codefresh
- Add encrypted environment variables for aws credentials.
     * AWS_ACCESS_KEY_ID
     * AWS_SECRET_ACCESS_KEY
- Add "deploy to ecs" step to codefresh.yml which runs codefresh/cf-deploy-ecs image with command cfecs-update
  Specify the aws region, ecs cluster and service names. See `cfecs-update -h` for parameter references

```yaml
# codefresh.yml example with deploy to ecs step
version: '1.0'

steps:
  build-step:
    type: build
    image-name: repo/image:tag

  push to registry:
    type: push
    candidate: ${{build-step}}
    tag: ${{CF_BRANCH}}

  deploy to ecs:
    image: codefreshplugins/cf-deploy-ecs
    commands:
      - cfecs-update <aws-region> <ecs-cluster-name> <ecs-service-name>
    environment:
      - AWS_ACCESS_KEY_ID=${{AWS_ACCESS_KEY_ID}}
      - AWS_SECRET_ACCESS_KEY=${{AWS_SECRET_ACCESS_KEY}}

    when:
      - name: "Execute for 'master' branch"
        condition: "'${{CF_BRANCH}}' == 'master'"
```


### Deployment Flow
- get ECS service by specified aws region, ecs cluster and service names
- create new revision from current task definition of the service. If --image-name and --image-tag are provided, replace the tag of the image
- launch update-service with new task definition revision
- wait for deployment to complete (by default, if running withou --no-wait)
    * deployment is considered as completed successfully if runningCount == desiredCount for PRIMARY deployment - see `aws ecs describe-service`
    * cfecs-update exits with timeout if after --timeout (default = 900s) runningCount != desiredCount script exits with timeout
    * cfecs-update exits with error if --max-failed (default = 2) or more ecs tasks were stopped with error for the task definition being deployed.
      ECS retries failed tasks continuously

### Usage with docker

```bash
docker run --rm -it -e AWS_ACCESS_KEY_ID=**** -e AWS_SECRET_ACCESS_KEY=**** codefresh/cf-ecs-deploy cfecs-update [options] <aws-region> <ecs-cluster-name> <ecs-service-name>
```

### cfecs-update -h
```
usage: cfecs-update [-h] [-i IMAGE_NAME] [-t IMAGE_TAG] [--wait | --no-wait]
                    [--timeout TIMEOUT] [--max-failed MAX_FAILED] [--debug]
                    region_name cluster_name service_name

Codefresh ECS Deploy

positional arguments:
  region_name           AWS Region, ex. us-east-1
  cluster_name          ECS Cluster Name
  service_name          ECS Service Name

optional arguments:
  -h, --help            show this help message and exit
  --wait                Wait for deployment to complete (default)
  --no-wait             No Wait for deployment to complete
  --timeout TIMEOUT     deployment wait timeout (default 900s)
  --max-failed MAX_FAILED
                        max failed tasks to consider deployment as failed
                        (default 2)
  --debug               show debug messages

  -i IMAGE_NAME, --image-name IMAGE_NAME
                        Image Name in ECS Task Definition to set new tag
  -t IMAGE_TAG, --image-tag IMAGE_TAG
                        Tag for the image
```