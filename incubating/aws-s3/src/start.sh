#!/bin/bash

# Test for SA being set
if [ -z ${AWS_ROLE_ARN+x} ];
then
  if [ -z ${S3_INTEGRATION+x} ] ;then
    echo "You must set S3_INEGRATION or associate a Service Account to your pipeline"
    exit 1
  else
    export AWS_ACCESS_KEY_ID=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.accessKeyId')
    export AWS_SECRET_ACCESS_KEY=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.secretAccessKey')
  fi
else
  echo "Service Account is set. Ignoring S3_INTEGRATION if defined."  
fi

export AWS_DEFAULT_REGION=$(echo "${REGION,,}")
export AWS_PAGER=""

cd $working_directory
echo "Starting to upload files to S3"
echo ""

if [ -d $SOURCE ]; then
  aws s3 cp $SOURCE s3://$BUCKET/$S3_PREFIX --recursive
else
  aws s3 cp $SOURCE s3://$BUCKET/$S3_PREFIX
fi

if [ $? -ne 0 ] ; then
  echo "Error uploading $SOURCE to s3://$BUCKET/$S3_PREFIX"
  exit 1
fi

echo ""
echo "Finished uploading files to S3"
echo ""

export uploadToS3_CF_OUTPUT_URL="https://s3.console.aws.amazon.com/s3/buckets/$BUCKET?region=$AWS_DEFAULT_REGION&prefix=$S3_PREFIX/"

echo "Files have been upload to: "
echo $uploadToS3_CF_OUTPUT_URL
echo ""

cf_export uploadToS3_CF_OUTPUT_URL
