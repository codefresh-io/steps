## Overview

The step allows to deploy to Amazon ECS Service that uses CodeDeploy to manage Blue/Green deployments.  

## Requirements
- ECS service with the **CODE\_DEPLOY** deployment controller;
- AWS Application Load Balancer with two target groups;
- CodeDeploy application and deployment group;
- [CodeDeploy IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/codedeploy_IAM_role.html);
- [ECS task execution IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html);
- _AWS\_ACCESS\_KEY\_ID_ and _AWS\_SECRET\_ACCESS\_KEY_;

## Demo environment
See the [prepare.sh](resources/prepare.sh) script to create test AWS resources.  

The following variables in the `defaults()` function should be updated regarding to your case:
- `PREFIX`;
- `APPLICATION\_PORT`;
- `APPLICATION_IMAGE`;
- `AWS_REGION`;
- `VPC_ID`;
- `AWS_SUBNET_A`;
- `AWS_SUBNET_B`;
- `ECS_CLUSTER_NAME`;

To run the script:
```
./prepare.sh
```

## The step usage
What the step does
- gets the current task definition;
- updates it with the new image;
- generates app spec yaml file;
- triggers a new deploy.

The step arguments:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `CLUSTER_NAME`
- `SERVICE_NAME`
- `CODEDEPLOY_APPLICATION`
- `CODEDEPLOY_DEPLOYMENT_GROUP`

