AWS_ACCESS_KEY_ID=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.accessKeyId')
AWS_SECRET_ACCESS_KEY=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.secretAccessKey')
AWS_DEFAULT_REGION=$(echo "${REGION,,}")
AWS_PAGER=""
KEY=$(echo $S3PREFIX/$CF_BUILD_ID)

cd $working_directory

aws s3 cp $SOURCE s3://$BUCKET/$S3PREFIX --recursive

export CF_OUTPUT_URL="https://s3.console.aws.amazon.com/s3/buckets/$BUCKET?region=$AWS_DEFAULT_REGION&prefix=$KEY/"

echo "Files have been upload to: \n\n$CF_OUTPUT_URL \n"

cf_export CF_OUTPUT_URL
