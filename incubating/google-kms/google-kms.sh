#!/bin/bash

for pluginVar in KMS_PROJECT KMS_LOCATION KMS_KEYRING KMS_KEY
    do
        if [ -z ${!pluginVar} ]; then echo $pluginVar is not set, stopping...; exit 1; fi
    done

echo $GCP_SA_KEY > google-app-creds.json
export GOOGLE_APPLICATION_CREDENTIALS=$(realpath google-app-creds.json)
operation=$1


function encrypt () {

    hashedtext=$(echo $2 | base64 | tr -d '\n') 
    cf_export $1=$(curl -s -X POST "https://cloudkms.googleapis.com/v1/projects/$KMS_PROJECT/locations/$KMS_LOCATION/keyRings/$KMS_KEYRING/cryptoKeys/$KMS_KEY:encrypt" \
        -d "{\"plaintext\":\"$hashedtext\"}" \
        -H "Authorization:Bearer $(gcloud auth application-default print-access-token)" \
        -H "Content-Type:application/json" | jq '.ciphertext' --raw-output )

    }

function decrypt {

	cf_export $1=$(curl -s -X POST "https://cloudkms.googleapis.com/v1/projects/$KMS_PROJECT/locations/$KMS_LOCATION/keyRings/$KMS_KEYRING/cryptoKeys/$KMS_KEY:decrypt" \
        -d "{\"ciphertext\":\"$2\"}" \
        -H "Authorization:Bearer $(gcloud auth application-default print-access-token)" \
        -H "Content-Type:application/json" | jq '.plaintext' --raw-output | base64 -d)
    
    }

for secret in "${@: 2}"
    do
        $operation $secret ${!secret}
    done
