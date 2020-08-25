#!/usr/bin/env bash

healthcheck(){
    echo "[CANARY INFO] Starting healthcheck"
    h=true

    #Start custom healthcheck
    output=$(kubectl get pods -l app="$CANARY_DEPLOYMENT" -n $NAMESPACE --no-headers)
    echo "[CANARY HEALTH] $output"
    s=($(echo "$output" | awk '{s+=$4}END{print s}'))
    c=($(echo "$output" | wc -l))

    if [ "$s" -gt "2" ]; then
        h=false
    fi
    ##if [ "$c" -lt "1" ]; then
    ##    h=false
    ##fi
    #End custom healthcheck

    if [ ! $h == true ]; then
        cancel
        echo "[CANARY HEALTH] Canary is unhealthy"
    else
        echo "[CANARY HEALTH] Service healthy."
    fi
}

runpipeline(){
    PARMS=""
    if [ ! -z "${TRIGGER_ID}" ]; then 
        PARMS+=" -t ${TRIGGER_ID} "
    fi

    if [ ! -z "${BRANCH}" ]; then
        PARMS+=" -b ${BRANCH} "
    fi

    if [ ! -z "${SHA}" ]; then 
        PARMS+=" -s ${SHA} "
    fi

    if [ ! -z "${NO_CACHE}" ]; then
        PARMS+=" --no-cache ${NO_CACHE} "
    fi
    
    if [ ! -z "${NO_CF_CACHE}" ]; then
        PARMS+=" --no-cf-cache ${NO_CF_CACHE} "
    fi

    if [ ! -z "${RESET_VOLUME}" ]; then
        PARMS+=" --reset-volume ${RESET_VOLUME} "
    fi

    PARMS+=" --variable SERVICE_NAME=$SERVICE_NAME "
    PARMS+=" --variable DEPLOYMENT_NAME=$DEPLOYMENT_NAME "
    PARMS+=" --variable CURRENT_VERSION=$CURRENT_VERSION "
    PARMS+=" --variable NEW_VERSION=$NEW_VERSION "
    PARMS+=" --variable PROD_DEPLOYMENT=$PROD_DEPLOYMENT "
    PARMS+=" --variable CANARY_DEPLOYMENT=$CANARY_DEPLOYMENT "
    PARMS+=" --variable NAMESPACE=$NAMESPACE "
    PARMS+=" --variable KUBE_CONTEXT=$KUBE_CONTEXT "

    echo "Running codefresh pipeline for canary analysis"
    echo "codefresh run $PIPELINE_ID $PARMS"
    codefresh run $PIPELINE_ID $PARMS
    if [ $? -eq 0 ]; then
        echo "Pipeline ran validation successfully"
    else
        echo "Pipeline failed with non-zero exit code - rolling back Canary Deployment"
        cancel
    fi
}

cancel(){
    echo "[CANARY] Cancelling rollout - healthcheck failed"

    echo "[CANARY SCALE] Restoring original deployment to $PROD_DEPLOYMENT"
    kubectl apply --force -f $WORKING_VOLUME/original_deployment.yaml -n $NAMESPACE
    kubectl rollout status deployment/$PROD_DEPLOYMENT -n $NAMESPACE

    #we could also just scale to 0.
    echo "[CANARY DELETE] Removing canary deployment completely"
    kubectl delete deployment $CANARY_DEPLOYMENT -n $NAMESPACE

    echo "[CANARY DELETE] Removing canary horizontal pod autoscaler completely"
    kubectl delete hpa $CANARY_DEPLOYMENT -n $NAMESPACE

    exit 1
}

cleanup(){
    echo "[CANARY CLEANUP] removing previous deployment $PROD_DEPLOYMENT"
    kubectl delete deployment $PROD_DEPLOYMENT -n $NAMESPACE

    echo "[CANARY CLEANUP] removing previous horizontal pod autoscaler $PROD_DEPLOYMENT"
    kubectl delete hpa $PROD_DEPLOYMENT -n $NAMESPACE

    echo "[CANARY CLEANUP] marking canary as new production"
    kubectl get service $SERVICE_NAME -o=yaml --namespace=${NAMESPACE} | sed -e "s/$CURRENT_VERSION/$NEW_VERSION/g" | kubectl apply --namespace=${NAMESPACE} -f -
}

incrementservice(){
    percent=$1
    starting_replicas=$2

    #debug
    #echo "Increasing canaries to $percent percent, max replicas is $starting_replicas"

    prod_replicas=$(kubectl get deployment $PROD_DEPLOYMENT -n $NAMESPACE -o=jsonpath='{.spec.replicas}')
    canary_replicas=$(kubectl get deployment $CANARY_DEPLOYMENT -n $NAMESPACE -o=jsonpath='{.spec.replicas}')
    echo "[CANARY INFO] Production has now $prod_replicas replicas, canary has $canary_replicas replicas"

    # This gets the floor for pods, 2.69 will equal 2
    let increment="($percent*$starting_replicas*100)/(100-$percent)/100"

    echo "[CANARY INFO] We will increment canary and decrease production for $increment replicas"

    let new_prod_replicas="$prod_replicas-$increment"
    #Sanity check
    if [ "$new_prod_replicas" -lt "0" ]; then
            new_prod_replicas=0
    fi

    let new_canary_replicas="$canary_replicas+$increment"
    #Sanity check
    if [ "$new_canary_replicas" -ge "$starting_replicas" ]; then
            new_canary_replicas=$starting_replicas
            new_prod_replicas=0
    fi

    echo "[CANARY SCALE] Setting canary replicas to $new_canary_replicas"
    kubectl -n $NAMESPACE scale --replicas=$new_canary_replicas deploy/$CANARY_DEPLOYMENT

    echo "[CANARY SCALE] Setting production replicas to $new_prod_replicas"
    kubectl -n $NAMESPACE scale --replicas=$new_prod_replicas deploy/$PROD_DEPLOYMENT

    #Wait a bit until production instances are down. This should always succeed
    kubectl -n $NAMESPACE rollout status deployment/$PROD_DEPLOYMENT

    #Calulate increments. N = the number of starting pods, I = Increment value, X = how many pods to add
    # x / (N + x) = I
    # Starting pods N = 5
    # Desired increment I = 0.35
    # Solve for X
    # X / (5+X)= 0.35
    # X = .35(5+x)
    # X = 1.75 + .35x
    # X-.35X=1.75
    # .65X = 1.75
    # X = 35/13
    # X = 2.69
    # X = 3
    # 5+3 = 8 #3/8 = 37.5%
    # Round		A 	B
    # 1			5	3
    # 2			2	6
    # 3			0	5
}

copy_deployment(){
    #Replace old deployment name with new
    sed -Ei -- "s/name\: $PROD_DEPLOYMENT/name: $CANARY_DEPLOYMENT/g" $WORKING_VOLUME/canary_deployment.yaml
    echo "[CANARY INFO] Replaced deployment name"

    #Replace docker image
    sed -Ei -- "s/$CURRENT_VERSION/$NEW_VERSION/g" $WORKING_VOLUME/canary_deployment.yaml
    echo "[CANARY INFO] Replaced image name"
    echo "[CANARY INFO] Production deployment is $PROD_DEPLOYMENT, canary is $CANARY_DEPLOYMENT"
}

input_deployment(){
    #Ouput user provided yml file to use as deployment object
    echo "${INPUT_DEPLOYMENT}" > ${WORKING_VOLUME}/canary_deployment.yaml
}

mainloop(){
    ANALYSIS_TYPE="${ANALYSIS_TYPE}"    
    if [ $ANALYSIS_TYPE = "PIPELINE" ]; then
        # List of variables for codefresh run usage
        PIPELINE_VARS=(
            PIPELINE_ID
            TRIGGER_ID
            BRANCH
            SHA
            NO_CACHE
            NO_CF_CACHE
            RESET_VOLUME
        )
        # Verify that the passed in variables actually have values and clean them
        for var in ${PIPELINE_VARS[*]}; do
            if ( echo "${!var}" | grep '${{' &>/dev/null ); then eval $var=""; fi
        done
        [ -z "${PIPELINE_ID}" ] &&  err "ANALYSIS_TYPE set to PIPELINE, must pass PIPELINE_ID"        
    fi      

    echo "[CANARY INFO] Selecting Kubernetes cluster"
    kubectl config use-context "${KUBE_CONTEXT}"

    echo "[CANARY INFO] Locating current version"
    CURRENT_VERSION=$(kubectl get service $SERVICE_NAME -o=jsonpath='{.metadata.labels.version}' --namespace=${NAMESPACE})

    if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
       echo "[DEPLOY NOP] NEW_VERSION is same as CURRENT_VERSION. Both are at $CURRENT_VERSION"
       exit 0
    fi

    echo "[CANARY INFO] current version is $CURRENT_VERSION"
    PROD_DEPLOYMENT=$DEPLOYMENT_NAME-$CURRENT_VERSION

    echo "[CANARY INFO] Locating current deployment"
    kubectl get deployment $PROD_DEPLOYMENT -n $NAMESPACE -o=yaml > $WORKING_VOLUME/canary_deployment.yaml

    echo "[CANARY INFO] keeping a backup of original deployment"
    cp $WORKING_VOLUME/canary_deployment.yaml $WORKING_VOLUME/original_deployment.yaml

    echo "[CANARY INFO] Reading current docker image"
    IMAGE=$(kubectl get deployment $PROD_DEPLOYMENT -n $NAMESPACE -o=yaml | grep image: | sed -E 's/.*image: (.*)/\1/')
    echo "[CANARY INFO] found image $IMAGE"
    echo "[CANARY INFO] Finding current replicas"

    if [[ -n ${INPUT_DEPLOYMENT} ]]; then
        #Allow user to provide custom new yaml deployment object
        input_deployment

        if ! STARTING_REPLICAS=$(grep "replicas:" < ${WORKING_VOLUME}/canary_deployment.yaml | awk '{print $2}'); then
            echo "[CANARY INFO] Failed getting replicas from input file: ${WORKING_VOLUME}/canary_deployment.yaml"
            echo "[CANARY INFO] Using the same number of replicas from prod deployment"
            STARTING_REPLICAS=$(kubectl get deployment $PROD_DEPLOYMENT -n $NAMESPACE -o=jsonpath='{.spec.replicas}')
        fi
    else
        #Copy existing deployment and update image only
        copy_deployment

        STARTING_REPLICAS=$(kubectl get deployment $PROD_DEPLOYMENT -n $NAMESPACE -o=jsonpath='{.spec.replicas}')
        echo "[CANARY INFO] Found replicas $STARTING_REPLICAS"
    fi

    #Start with one replica
    sed -Ei -- "s#replicas: $STARTING_REPLICAS#replicas: 1#g" $WORKING_VOLUME/canary_deployment.yaml
    echo "[CANARY INIT] Launching 1 pod with canary"

    #Launch canary
    kubectl apply -f $WORKING_VOLUME/canary_deployment.yaml -n $NAMESPACE

    echo "[CANARY INFO] Awaiting canary pod..."
    while [ $(kubectl get pods -l app="$CANARY_DEPLOYMENT" -n $NAMESPACE --no-headers | wc -l) -eq 0 ]
    do
      sleep 2
    done

    echo "[CANARY INFO] Canary target replicas: $STARTING_REPLICAS"


    # Conditional logic to either call a pipeline or execute the health check
    if [ $ANALYSIS_TYPE = "PIPELINE" ]; then        
        while [ $TRAFFIC_INCREMENT -lt 100 ]
        do
            p=$((p + $TRAFFIC_INCREMENT))
            if [ "$p" -gt "100" ]; then
                p=100
            fi
            echo "[CANARY INFO] Rollout is at $p percent"

            incrementservice $TRAFFIC_INCREMENT $STARTING_REPLICAS

            if [ "$p" == "100" ]; then
                cleanup
                echo "[CANARY INFO] Done"
                exit 0
            fi
            echo "[CANARY INFO] Will now sleep for $SLEEP_SECONDS seconds"
            sleep $SLEEP_SECONDS

            # Execute a pipeline run for every increment to verify health in some way
            runpipeline            
        done        
    else
        healthcheck

        while [ $TRAFFIC_INCREMENT -lt 100 ]
        do
            p=$((p + $TRAFFIC_INCREMENT))
            if [ "$p" -gt "100" ]; then
                p=100
            fi
            echo "[CANARY INFO] Rollout is at $p percent"

            incrementservice $TRAFFIC_INCREMENT $STARTING_REPLICAS

            if [ "$p" == "100" ]; then
                cleanup
                echo "[CANARY INFO] Done"
                exit 0
            fi
            echo "[CANARY INFO] Will now sleep for $SLEEP_SECONDS seconds"
            sleep $SLEEP_SECONDS
            healthcheck
        done
    fi    
}

if [ "$1" != "" ] && [ "$2" != "" ] && [ "$3" != "" ] && [ "$4" != "" ] && [ "$5" != "" ] && [ "$6" != "" ] && [ "$7" != "" ]; then
    WORKING_VOLUME=${1%/}
    SERVICE_NAME=$2
    DEPLOYMENT_NAME=$3
    TRAFFIC_INCREMENT=$4
    NAMESPACE=$5
    NEW_VERSION=$6
    SLEEP_SECONDS=$7
    CANARY_DEPLOYMENT=$DEPLOYMENT_NAME-$NEW_VERSION
else
    echo "USAGE\n k8s-canary-rollout.sh [WORKING_VOLUME] [SERVICE_NAME] [DEPLOYMENT_NAME] [TRAFFIC_INCREMENT] [NAMESPACE] [NEW_VERSION] [SLEEP_SECONDS]"
    echo "\t [WORKING_VOLUME] - This should be set with \${{CF_VOLUME_PATH}}"
    echo "\t [SERVICE_NAME] - Name of the current service"
    echo "\t [DEPLOYMENT_NAME] - The name of the current deployment"
    echo "\t [TRAFFIC_INCREMENT] - Integer between 1-100 that will step increase traffic"
    echo "\t [NAMESPACE] - Namespace of the application"
    echo "\t [NEW_VERSION] - The next version of the Docker image"
    echo "\t [SLEEP_SECONDS] - seconds to wait for each canary step"
    exit 1;
fi

echo $BASH_VERSION

mainloop
