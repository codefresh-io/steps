# based on the work from Vu duration
# https://dev.to/vumdao/create-aws-cdk-image-container-43ei

FROM amazon/aws-lambda-python:3.8

ENV AWS_CDK_VERSION=1.91.0
ENV AWS_DEFAULT_REGION=us-east-1

RUN yum -y update && \
    curl -sL https://rpm.nodesource.com/setup_12.x | bash - && \
    yum list available nodejs && \
    yum install -y python3-pip && \
    yum install -y nodejs && \
    npm install -g aws-cdk@${AWS_CDK_VERSION} && \
    pip3 install aws-cdk.aws-ec2 aws-cdk.aws-route53 aws-cdk.aws-iam aws-cdk.aws-elasticloadbalancingv2 aws-cdk.core

#CMD ["cdk version"]
CMD ["/bin/env"]
