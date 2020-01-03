#!/usr/bin/env bash

# DESCRIPTION

# Requirements
# - AWS VPC
# - AWS ECS CLUSTER

# To be created
# - AWS Security Group
# - AWS Load Balancer
# - AWS ECS Task Definition
# - AWS ECS Service
# - AWS Code Deploy application
# - AWS Code Deploy Deployment Group

defaults() {
# VARIABLES
##################################################################

# To update
  PREFIX="ecs-bg-update"
  APPLICATION_PORT="8081"
  APPLICATION_IMAGE="${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/simple-server:latest"

# Defaults related to Codefresh
  AWS_REGION="us-east-2"

  ECS_CLUSTER_NAME="fargatedemo"
  ECS_SERVICE_NAME="${PREFIX}-service"
  ECS_SERVICE_ARN=""
  TASK_DEFINITION_FAMILY="${PREFIX}-td"
  TASK_DEFINITION_ARN_LATEST=""
  CONTAINER_NAME="${PREFIX}-app"
  EXECUTION_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole"

  VPC_ID="vpc-0a50cbcc947d3da2a"
  AWS_SUBNET_A="subnet-0f487eefd0c4172e0"
  AWS_SUBNET_B="subnet-03f1316aae259bd59"
  AWS_SECURRITY_GROUP_NAME="${PREFIX}-sg"
  AWS_SECURRITY_GROUP_ID=""

  AWS_LB_NAME="${PREFIX}-bg-alb"
  AWS_LB_ARN=""
  AWS_LB_LISTENER_ARN=""
  TARGET_GROUP_NAME_1="${PREFIX}-tg-1"
  TARGET_GROUP_ARN_1=""
  TARGET_GROUP_NAME_2="${PREFIX}-tg-2"
  TARGET_GROUP_ARN_2=""

  CODEDEPLOY_SERVICE_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecs-plugin-codedeploy"
  CODEDEPLOY_APPLICATION_NAME="AppECS-${ECS_CLUSTER_NAME}-${ECS_SERVICE_NAME}"
  CODEDEPLOY_DEPLOYMENT_GROUP_NAME="DgpECS-${ECS_CLUSTER_NAME}-${ECS_SERVICE_NAME}"
  CODEDEPLOY_READY_TIMEOUT=0 # Time in minutes to wait before switching to green
  CODEDEPLOY_BLUE_TERMINATE_TIMEOUT=5  # Time in minutes to wait to terminate blue instance
}

##################################################################

set -e
set -o pipefail

echoSection() {
  printf -- "--------------------------------------------\n\n"
  printf  "\n\n[INFO] $1\n\n"
}

assert_not_empty() {
  local readonly var_name="$1"
  # declare -p "$var_name" &>/dev/null
  declare -p "$var_name" 
}

assert_is_installed() {
  local readonly name="$1"
  if [[ ! $(command -v ${name}) ]]; then
    echo "ERROR: The binary '$name' is required by this script but is not installed or in the system's PATH."
    exit 1
  fi
}

aws_get_account_id() {
  echoSection "Get account id"
  AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)
  assert_not_empty AWS_ACCOUNT_ID
}

aws_create_security_group() {
  echoSection "Create new security group"
  AWS_SECURRITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=vpc-id,Values=${VPC_ID} Name=group-name,Values=${AWS_SECURRITY_GROUP_NAME} --query "SecurityGroups[*].{ID:GroupId}"  | jq -r .[0].ID)
  if [ "$AWS_SECURRITY_GROUP_ID" == "null" ]; then
    AWS_SECURRITY_GROUP_ID=$(aws ec2 create-security-group --group-name ${AWS_SECURRITY_GROUP_NAME} --description "Test blue/green deployment" --vpc-id ${VPC_ID} | jq -r .GroupId)
    assert_not_empty AWS_SECURRITY_GROUP_ID 
    aws ec2 authorize-security-group-ingress --group-id $AWS_SECURRITY_GROUP_ID --protocol tcp --cidr 0.0.0.0/0 --port $APPLICATION_PORT
  fi

  assert_not_empty AWS_SECURRITY_GROUP_ID
}

aws_create_load_balancer() {
  echoSection "Create new AWS ALB"
  AWS_LB_ARN=$(aws elbv2 create-load-balancer \
     --name "${AWS_LB_NAME}" \
     --subnets ${AWS_SUBNET_A} ${AWS_SUBNET_B} \
     --security-groups ${AWS_SECURRITY_GROUP_ID} \
     --region ${AWS_REGION} | jq -r .LoadBalancers[0].LoadBalancerArn) 

  assert_not_empty AWS_LB_ARN 
}

aws_create_target_groups() {
  echoSection "Create new Target Group 1"
  export TARGET_GROUP_ARN_1=$(aws elbv2 create-target-group \
       --name ${TARGET_GROUP_NAME_1} \
       --protocol HTTP \
       --port ${APPLICATION_PORT} \
       --target-type ip \
       --vpc-id ${VPC_ID} \
       --region ${AWS_REGION} | jq -r .TargetGroups[0].TargetGroupArn)

  assert_not_empty TARGET_GROUP_ARN_1

  echoSection "Create Listener"
  AWS_LB_LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn ${AWS_LB_ARN} | jq -r .Listeners[0].ListenerArn)
  if [ "$AWS_LB_LISTENER_ARN" == "null" ]; then
    AWS_LB_LISTENER_ARN=$(aws elbv2 create-listener \
         --load-balancer-arn ${AWS_LB_ARN} \
         --protocol HTTP \
         --port ${APPLICATION_PORT} \
         --default-actions Type=forward,TargetGroupArn=${TARGET_GROUP_ARN_1} \
         --region ${AWS_REGION} | jq -r .Listeners[0].ListenerArn) 
  fi

  assert_not_empty AWS_LB_LISTENER_ARN

  echoSection "Create new Target Group 2"
  export TARGET_GROUP_ARN_2=$(aws elbv2 create-target-group \
       --name ${TARGET_GROUP_NAME_2} \
       --protocol HTTP \
       --port 80 \
       --target-type ip \
       --vpc-id ${VPC_ID} \
       --region ${AWS_REGION} | jq -r .TargetGroups[0].TargetGroupArn)

  assert_not_empty TARGET_GROUP_ARN_2
}

aws_register_task_definition() {
  echoSection "Register new task definition"
  TASK_DEFINITION_ARN_LATEST=$(aws ecs register-task-definition \
       --region ${AWS_REGION} \
       --family ${TASK_DEFINITION_FAMILY} \
       --network-mode "awsvpc" \
       --requires-compatibilities "FARGATE" \
       --cpu "256" \
       --memory "512" \
       --execution-role-arn ${EXECUTION_ROLE_ARN} \
       --container-definitions "[{\"name\": \"$CONTAINER_NAME\",\"image\": \"$APPLICATION_IMAGE\",\"portMappings\": [{\"containerPort\": $APPLICATION_PORT,\"hostPort\": $APPLICATION_PORT,\"protocol\": \"tcp\"}],\"essential\": true}]" | jq -r .taskDefinition.taskDefinitionArn)

  assert_not_empty TASK_DEFINITION_ARN_LATEST
}

aws_create_ecs_service() {
  echoSection "Create new ECS service"
  ECS_SERVICE_ARN=$(aws ecs describe-services --services ${ECS_SERVICE_NAME} --cluster ${ECS_CLUSTER_NAME} | jq -r .services[0].serviceArn)
  if [ "$ECS_SERVICE_ARN" == "null" ]; then
    aws ecs create-service \
      --cluster ${ECS_CLUSTER_NAME} \
      --service-name ${ECS_SERVICE_NAME} \
      --task-definition ${TASK_DEFINITION_FAMILY} \
      --desired-count 1 \
      --launch-type FARGATE \
      --platform-version LATEST \
      --desired-count 1 \
      --deployment-controller "type=CODE_DEPLOY" \
      --network-configuration "awsvpcConfiguration={subnets=["$AWS_SUBNET_A","$AWS_SUBNET_B"],securityGroups=["$AWS_SECURRITY_GROUP_ID"],assignPublicIp=ENABLED}" \
      --load-balancers "targetGroupArn=${TARGET_GROUP_ARN_1},containerName=${CONTAINER_NAME},containerPort=${APPLICATION_PORT}"

    ECS_SERVICE_ARN=$(aws ecs describe-services --services ${ECS_SERVICE_NAME} --cluster ${ECS_CLUSTER_NAME} | jq -r .services[0].serviceArn)
  fi

  assert_not_empty ECS_SERVICE_ARN
}

aws_create_codedeploy_application() {
  echoSection "Create new Code Deploy Application"
  local app_index=$(aws deploy list-applications | jq -c --arg appname "${CODEDEPLOY_APPLICATION_NAME}" '.applications | index( $appname )')
  if [ "$app_index" == "null" ]; then
    aws deploy create-application \
       --application-name ${CODEDEPLOY_APPLICATION_NAME} \
       --compute-platform ECS \
       --region ${AWS_REGION}
  fi
}

aws_create_codedeploy_deployment_group() {
  echoSection "Create new Code Deploy Deployment Group"
  local group_index=$(aws deploy list-deployment-groups --application-name ${CODEDEPLOY_APPLICATION_NAME} | jq -r --arg groupname "${CODEDEPLOY_DEPLOYMENT_GROUP_NAME}" '.deploymentGroups[0] | index( $groupname )')

  if [ "$group_index" == "null" ]; then
    aws deploy create-deployment-group \
       --region ${AWS_REGION} \
       --application-name ${CODEDEPLOY_APPLICATION_NAME} \
       --service-role-arn ${CODEDEPLOY_SERVICE_ROLE_ARN} \
       --deployment-group-name ${CODEDEPLOY_DEPLOYMENT_GROUP_NAME} \
       --blue-green-deployment-configuration "terminateBlueInstancesOnDeploymentSuccess={action=TERMINATE,terminationWaitTimeInMinutes="${CODEDEPLOY_BLUE_TERMINATE_TIMEOUT}"},deploymentReadyOption={actionOnTimeout=CONTINUE_DEPLOYMENT,waitTimeInMinutes="${CODEDEPLOY_READY_TIMEOUT}"}" \
       --auto-rollback-configuration "enabled=true,events=DEPLOYMENT_FAILURE,DEPLOYMENT_STOP_ON_REQUEST" \
       --deployment-style "deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL" \
       --ecs-services "serviceName=${ECS_SERVICE_NAME},clusterName=${ECS_CLUSTER_NAME}" \
       --load-balancer-info \
       "{
         \"targetGroupPairInfoList\": [{
           \"targetGroups\": [
             {
               \"name\": \"${TARGET_GROUP_NAME_1}\"
             },
             {
               \"name\": \"${TARGET_GROUP_NAME_2}\"
             }
           ],
           \"prodTrafficRoute\": {
             \"listenerArns\": [
               \"${AWS_LB_LISTENER_ARN}\"
             ]
           }
         }]
       }"
  fi
}

print_example() {
  echoSection "To run a new deploy"
  printf "\n\nCreate a app spec file:\n\n"
  echo "echo \"---
version: 1
Resources:
- TargetService:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: ${TASK_DEFINITION_ARN_LATEST}
      LoadBalancerInfo:
        ContainerName: ${CONTAINER_NAME}
        ContainerPort: ${APPLICATION_PORT}\" > /tmp/appspec.yaml"

  printf "\n\nRun a new deploy:\n\n"
  echo "aws ecs deploy \  
  --service ${ECS_SERVICE_NAME} \\
  --task-definition <path to task def json file> \\
  --codedeploy-appspec /tmp/appspec.yaml \\
  --cluster ${ECS_CLUSTER_NAME}"

}


# MAIN
main() {
  assert_is_installed aws
  assert_is_installed jq

  aws_get_account_id 

  defaults

  aws_create_security_group

  aws_create_load_balancer

  aws_create_target_groups

  aws_register_task_definition

  aws_create_ecs_service

  aws_create_codedeploy_application

  aws_create_codedeploy_deployment_group

  print_example

}

main $@
