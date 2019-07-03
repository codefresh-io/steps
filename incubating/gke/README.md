# Codefresh GKE plugin

Use Codefresh GKE plugin to create GKE Kubernetes cluster for integration tests 


## codefresh/plugin-gke Docker Image details

### Requirements:
  - set GOOGLE_SERVICE_ACCOUNT_KEY to the Google Service Account Key value
  - Service account should have enough permissions to create and operate GKE Cluster:
    Kubernetes Engine Admin or subset of privileges from GKE Developer+clusterAdmin  

### Environements:
  - GOOGLE_SERVICE_ACCOUNT_KEY - Google Service Account Key value, mandatory

  - CLOUDSDK_COMPUTE_ZONE - one of valid Google Compute zones - see https://cloud.google.com/compute/docs/regions-zones/
  - CLOUDSDK_COMPUTE_REGION - one of valid Google Compute regions. If both CLOUDSDK_COMPUTE_ZONE and CLOUDSDK_COMPUTE_REGION are not set, default is us-central1
  
  - GKE_CLUSTER_NAME - name of gke cluster to create  
  
  - Codefresh variables: https://docs.codefresh.io/docs/variables

### Commands: 

* `gke-create` - creates GKE cluster on Google Cloud project defined by GOOGLE_SERVICE_ACCOUNT_KEY
  - `gcloud container clusters create <GKE_CLUSTER_NAME> <optional parameters>`
  - sets kubectl current context to the newly created cluster for futher pipeline steps

* `gke-delete` - deletes GKE Cluster by name on Google Cloud project defined by GOOGLE_SERVICE_ACCOUNT_KEY
  
* `kubectl` - you can use it to operate on the created cluster 
* `gcloud`

#### Google Cloud Zone/Region note
`--zone=<zone>` or `--region=<region>` parameters are mandatory for `gcloud container clusters ...` commands
By default we are using default zone of us-central1 region
You can change it by specifying yours `--zone= | --region= ` or using `CLOUDSDK_COMPUTE_ZONE | CLOUDSDK_COMPUTE_ZONE` env vars
If you specified `--zone= | --region= ` for `gke-create` you must specify the same zone/region parameters for `gke-delete` 

## Usage

Set the environment variables and add the following step to your Codefresh pipeline:

```yaml
---
version: '1.0'

steps:
  # 
  create-cluster:
    image: codefreshplugins/plugin-gke
    commands: 
        - gke-create gke-test-cluster-1 --zone=us-central1-a --num-nodes 2 --machine-type n1-standard-2
    
  deploy-my-service:
    image: codefreshplugins/plugin-gke
    commands:
        - kubectl get pods --all-namespaces -owide
       # - deploy.sh
       # - kubectl run --image mytestimage
       # - check-status.sh

  clean:
     image: codefreshplugins/plugin-gke
     commands:
        - gke-delete gke-test-cluster-1 --zone=us-central1-a 

```