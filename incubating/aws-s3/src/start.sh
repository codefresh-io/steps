export AWS_ACCESS_KEY_ID=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.accessKeyId')
export AWS_SECRET_ACCESS_KEY=$(codefresh get context ${S3_INTEGRATION} --decrypt -o json |jq --raw-output '.spec.data.auth.jsonConfig.secretAccessKey')
export AWS_DEFAULT_REGION=$(echo "${REGION,,}")
export AWS_PAGER=""
cd $working_directory
echo "Starting to upload files to S3"
echo ""
aws s3 cp $SOURCEDIR s3://$BUCKET/$S3_PREFIX --recursive
echo ""
echo "Finished uplaoding files to S3"
echo ""
export uploadToS3_CF_OUTPUT_URL="https://s3.console.aws.amazon.com/s3/buckets/$BUCKET?region=$AWS_DEFAULT_REGION&prefix=$S3_PREFIX/"
echo "Files have been upload to: "
echo $uploadToS3_CF_OUTPUT_URL
echo ""
cf_export uploadToS3_CF_OUTPUT_URL
