#!/usr/bin/env bash
set -e

msg() { echo -e "\e[32mINFO [$(date +%F_%H-%M-%S)] ---> $1\e[0m"; }
yellow() { echo -e "\e[33m$1\e[0m"; }
err() { echo -e "\e[31mERR [$(date +%F_%H-%M-%S)] ---> $1\e[0m" ; exit 1; }

REQUIRED_VARS=(
    VAULT_ADDR
    VAULT_AUTH_METHOD
    VAULT_AUTH_TOKEN
    APPROLE_ROLE_ID
    APPROLE_SECRET_ID
    VAULT_PATH
    VAULT_PATH_DELIMITER
    VAULT_FIELD_NAME
    VAULT_VARIABLE_EXPORT_PREFIX    
    VAULT_CLIENT_CERT_BASE64
    VAULT_CLIENT_KEY_BASE64
)

# There might be values for cf empty vars, like ${{VAR}} substituted like this into
# the script. We want them to be really empty
for var in ${REQUIRED_VARS[*]}; do
    if ( echo "${!var}" | grep '${{' &>/dev/null ); then eval $var=""; fi
done

#### Checking for required values
[ -z "$VAULT_ADDR" ] && err "Need to set VAULT_ADDR"
echo "Vault URL is: $VAULT_ADDR"
[ -z "$VAULT_PATH" ] && err "Need to set VAULT_PATH"
# If an Auth method isn't passed, default to Token for backwards compatibility
if [ -z "$VAULT_AUTH_METHOD" ]; then
    msg "VAULT_AUTH_METHOD not set: using default Token auth mode"
    [ -z "$VAULT_AUTH_TOKEN" ] && err "Need to set VAULT_AUTH_TOKEN"
# If auth method of APPROLE is passed, verify the required values are populated
elif [ "$VAULT_AUTH_METHOD" = "APPROLE" ]; then
    msg "Authentication method set to APPROLE"
    [ -z "$APPROLE_ROLE_ID" ] && err "Need to set APPROLE_ROLE_ID"
    [ -z "$APPROLE_SECRET_ID" ] && err "Need to set APPROLE_SECRET_ID"
fi

if [ ! -z "$VAULT_CLIENT_CERT_BASE64" ]; then
   echo $VAULT_CLIENT_CERT_BASE64 | base64 -d > /client.cert.pem
   echo $VAULT_CLIENT_KEY_BASE64 | base64 -d > /client.key.pem
   chmod 700 /client.*
   export VAULT_CLIENT_CERT="/client.cert.pem"
   export VAULT_CLIENT_KEY="/client.key.pem"
fi

msg "Authenticating Vault"
# Setting default vault return output to JSON
export VAULT_FORMAT="json"

if [ "$VAULT_AUTH_METHOD" = "APPROLE" ]; then
    client_token=$(vault write auth/approle/login role_id=$APPROLE_ROLE_ID secret_id=$APPROLE_SECRET_ID | jq '.auth.client_token' -j)
    # Set the vault token for any future requests to the client token retrieved by the approle authentication
    export VAULT_TOKEN=$client_token
else
    vault login $VAULT_AUTH_TOKEN  >/dev/null
fi

if [ $? == 0 ]; then
  msg "You are successfully authenticated"
fi

msg "Reading provided path"

if [ ! -z "$VAULT_FIELD_NAME" ]; then
    field_return_value=$(vault kv get -format table -field $VAULT_FIELD_NAME $VAULT_PATH)
    echo $VAULT_VARIABLE_EXPORT_PREFIX$VAULT_FIELD_NAME=$field_return_value >> /meta/env_vars_to_export
else
    # If a path delimiter is specified, we need to break up the multiple paths and iterate over them
    if [ ! -z "$VAULT_PATH_DELIMITER" ]; then
        # Set the delimiter to the passed in delimiter value and break the string apart
        IFS=$VAULT_PATH_DELIMITER read -ra SPLIT_VAULT_PATHS <<< "$VAULT_PATH"
        for i in "${SPLIT_VAULT_PATHS[@]}"; do
            msg "Exporting variables from path $i"
            # Grab the json values from this path and add any prefix specified
            for s in $(vault kv get $i | jq -c '.data.data' | jq -r "to_entries|map(\"$VAULT_VARIABLE_EXPORT_PREFIX\(.key)=\(.value|tostring)\")|.[]" ); do                
                echo $s >> /meta/env_vars_to_export
            done
        done
    # Export values from a single path
    else
        msg "Exporting variables from path $VAULT_PATH"
        # Grab the json values from this path and add any prefix specified
        for s in $(vault kv get $VAULT_PATH | jq -c '.data.data' | jq -r "to_entries|map(\"$VAULT_VARIABLE_EXPORT_PREFIX\(.key)=\(.value|tostring)\")|.[]" ); do            
            echo $s >> /meta/env_vars_to_export
        done
    fi
    
fi


