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

fatal() {
    echo -e "\e[31m[FATAL] $1\e[0m"
    exit 1
}

log() {
    echo -e $1
}

warn() {
    echo -e "\e[33m[WARN] $1\e[0m"
}


log "Using Codefresh API: $PROTOCOL://$HOST"
log "Downloading audit log to $AUDIT_DEST"

if [ -z $CF_API_KEY ]
then
    fatal "CF_API_KEY is not set, exiting"
fi

if [ -z $GOOGLE_STORAGE ]
then
    fatal "GOOGLE_STORAGE is not set, exiting"
fi

if [ -z $GOOGLE_BUCKET_NAME ]
then
    fatal "GOOGLE_BUCKET_NAME is not set, exiting"
fi

log "Requesting Google context $GOOGLE_STORAGE from Codefresh aPI"
curl -o /tmp/ctx.json -H "Authorization: $CF_API_KEY" $ENDPOINT_GET_CONTEXT/$GOOGLE_STORAGE?decrypt=true
GOOGLE_SA_TMP_FILE="/tmp/google-sa.json"
jq -r ".spec.data.auth.jsonConfig" /tmp/ctx.json > $GOOGLE_SA_TMP_FILE

log "Testing authentication with Google:"
gcloud auth activate-service-account --key-file=$GOOGLE_SA_TMP_FILE
if [ -z $GOOGLE_PROJECT_ID ]
then
    warn "GOOGLE_PROJECT_ID is not set, trying to get it from $GOOGLE_SA_TMP_FILE .project_id"
    project=$(jq -r .project_id $GOOGLE_SA_TMP_FILE)
    if [ -z $project ]
    then
        fatal "Cannot find .project_id in $GOOGLE_SA_TMP_FILE, exiting"
    fi
    GOOGLE_PROJECT_ID=$project
    log "Using project-id $GOOGLE_PROJECT_ID"
    gcloud config set project $GOOGLE_PROJECT_ID
    log ""
fi

secondsToReduceFromNow=""
if [ -z $FILTER_TIME_RANGE ]
then
    log "FILTER_TIME_RANGE not set, ignoring"
else
    log "FILTER_TIME_RANGE is set to $FILTER_TIME_RANGE"
    case $FILTER_TIME_RANGE in
        1h)
            log "1h match"
            secondsToReduceFromNow="3600"
            ;;
        2h)
            log "2h match"
            secondsToReduceFromNow="7200"
            ;;
        8h)
            log "8h match"
            secondsToReduceFromNow="28800"
            ;;
        16h)
            log "16h match"
            secondsToReduceFromNow="57600"
            ;;
        24h)
            log "24h match"
            secondsToReduceFromNow="86400"
            ;;
        *)
            fatal "FILTER_TIME_RANGE is set but dosen't not matched, supported [1h, 2h, 8h, 16h, 24h]"
            ;;
    esac
fi

QUERY="?"
if [ -z $FILTER_TIME_FROM ]
then
    # in case the FILTER_TIME_RANGE was not set and FILTER_TIME_FROM is not set, calculate last 24 hours
    if [ eq $secondsToReduceFromNow "" ]
    then
        secondsToReduceFromNow="86400"
    fi
    now=$(date +%s)
    FILTER_TIME_TO=$(($now * 1000))
    FILTER_TIME_FROM=$((($now - $secondsToReduceFromNow) * 1000))
else
    log "FILTER_TIME_FROM is set, FILTER_TIME_FROM=$FILTER_TIME_FROM"

fi
QUERY="$QUERY&from=$FILTER_TIME_FROM"

if [ -z $FILTER_TIME_TO ]
then
    defaultFilterTimeTo=$(($(date +%s) * 1000 ))
    debug "FILTER_TIME_TO is not set, using default: $defaultFilterTimeTo"
    FILTER_TIME_TO=$defaultFilterTimeTo
else
    log "FILTER_TIME_TO is set, FILTER_TIME_TO=$FILTER_TIME_TO"
fi
QUERY="$QUERY&to=$FILTER_TIME_TO"

log "Calling Codefresh API: $ENDPOINT_DOWNLOAD?$QUERY"
curl -o $AUDIT_DEST -H "Authorization: $CF_API_KEY" "$ENDPOINT_DOWNLOAD?$QUERY"
log "Audit log download completed" 

if [ -z $DATE_FORMAT ]
then
    format="%m-%d-%y"
    warn "DATE_FORMAT is not set, using default format: $format"
    DATE_FORMAT=$format
fi

name="codefresh-audit-$(date +$DATE_FORMAT)-from-$FILTER_TIME_FROM-to-$FILTER_TIME_TO"
log "Upload $name to $GOOGLE_BUCKET_NAME"

gsutil mv $AUDIT_DEST gs://$GOOGLE_BUCKET_NAME/$name

echo "Upload completed"