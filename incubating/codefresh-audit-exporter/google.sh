#!/usr/bin/env sh

set -e

# set defaults
HOST=${CF_HOST:-g.codefresh.io}
PROTOCOL=${CF_PROTOCOL:-"https"}

# endpoint where to get the audit
ENDPOINT_DOWNLOAD=$PROTOCOL://$HOST/api/audit/download
ENDPOINT_GET_CONTEXT=$PROTOCOL://$HOST/api/contexts
DEFAULT_DESTINATION="/tmp/audit.csv"
AUDIT_DEST=${AUDIT_DESTINATION:-$DEFAULT_DESTINATION}

echo "Using Codefresh API: $PROTOCOL://$HOST"
echo "Downloading audit log to $AUDIT_DEST"

if [ -z $CF_API_KEY ]
then
    echo "CF_API_KEY is not set, exiting"
    exit 1
fi

if [ -z $GOOGLE_STORAGE ]
then
    echo "GOOGLE_STORAGE is not set, exiting"
    exit 1
fi

if [ -z $GOOGLE_BUCKET_NAME ]
then
    echo "GOOGLE_BUCKET_NAME is not set, exiting"
    exit 1
fi

echo "Requesting Google context $GOOGLE_STORAGE from Codefresh aPI"
curl -o /tmp/ctx.json -H "Authorization: $CF_API_KEY" $ENDPOINT_GET_CONTEXT/$GOOGLE_STORAGE?decrypt=true
GOOGLE_SA_TMP_FILE="/tmp/google-sa.json"
jq -r ".spec.data.auth.jsonConfig" /tmp/ctx.json > $GOOGLE_SA_TMP_FILE

echo "Testing authentication with Google:"
gcloud auth activate-service-account --key-file=$GOOGLE_SA_TMP_FILE
if [ -z $GOOGLE_PROJECT_ID ]
then
    echo "GOOGLE_PROJECT_ID is not set, trying to get it from $GOOGLE_SA_TMP_FILE .project_id"
    project=$(jq -r .project_id $GOOGLE_SA_TMP_FILE)
    if [ -z $project ]
    then
        echo "Cannot find .project_id in $GOOGLE_SA_TMP_FILE, exiting"
        exit 1
    fi
    GOOGLE_PROJECT_ID=$project
    echo "Using project-id $GOOGLE_PROJECT_ID"
    gcloud config set project $GOOGLE_PROJECT_ID
    echo ""
fi

curl -o $AUDIT_DEST -H "Authorization: $CF_API_KEY" $ENDPOINT_DOWNLOAD
echo "Audit log download completed"

if [ -z $DATE_FORMAT ]
then
    format="%m-%d-%y"
    echo "DATE_FORMAT is not set, using default format: $format"
    DATE_FORMAT=$format
fi

name="codefresh-audit-$(date +$DATE_FORMAT)"
echo "Upload $name to $GOOGLE_BUCKET_NAME"

gsutil mv $AUDIT_DEST gs://$GOOGLE_BUCKET_NAME/$name

echo "Upload completed"