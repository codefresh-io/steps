# Kubernetes deployment with canaries

This repository holds a bash script that allows you to perform canary deployments on a Kubernetes cluster.
It is part of the respective [Codefresh blog post](https://codefresh.io/kubernetes-tutorial/fully-automated-canary-deployments-kubernetes/)

## Description

The script expects you to have an existing deployment and service on your K8s cluster. It does the following:

1. Reads the existing deployment from the cluster to a yml file
1. Changes the name of the deployment and the docker image to a new version 
1. Deploys 1 replica for the new version (the canary)
1. Waits for some time (it is configurable) and checks the number of restarts
1. If everything is ok it adds more canaries and scales down the production instances
1. The cycle continues until all replicas used by the service are canaries (the production replicas are zero)

If something goes wrong (the pods have restarts) the scripts deletes all canaries and scales
back the production version to the original number of replicas


Of course during the wait period when both deployments are active, you are free to run your own additional
checks or integration tests to see if the new deployment is ok.

The canary percentage is configurable. The script will automatically calculate the phase

Example:

 * Production instance has 5 replicas
 * User enters canary waves to 35%
 * Script calculates 35% is about 2 pods
 
 | Phase | Production | Canary |
 | ------------- | ------------- |------|
 | Original | 5 | 0 |
 | A  | 5  |1 |
 | B    | 3 | 3 |
 | C    | 1 | 5 |
 | Final    | 0 | 5 |

## Prerequisites

As a convention the script expects

1. The name of your deployment to be $APP_NAME-$VERSION
1. Your service has a metadata label that shows which deployment is currently "in production"

Notice that the new color deployment created by the script will follow the same conventions. This
way each subsequent pipeline you run will work in the same manner.

You can see examples of the labels with the sample application:

* [service](example/service.yml)
* [deployment](example/deployment.yml)

## How to use the script on its own

The script needs one environment variable called `KUBE_CONTEXT` that selects the K8s cluster that will be used (if you have more than one)

The rest of the parameters are provided as command line arguments

| Parameter | Argument Number | Description     |
| ----------| --------------- | --------------- |
| Working directory   |         1       | Folder used for temp/debug files |
| Service   |         2      | Name of the existing service |
| Deployment |        3       | Name of the existing deployment |
| Traffic increment |   4        | Percentage of pods to convert to canaries at each stage |  
| Namespace |     5           | Kubernetes namespace that will be used |
| New version |       6       | Tag of the new docker image    |
| Health seconds | 7          | Time to wait before each canary stage |


Here is an example:

```
./k8s-canary-rollout.sh myService myApp 20 my-namespace 73df943 30 
```

## How to do Canary deployments in Codefresh

The script also comes with a Dockerfile that allows you to use it as a Docker image in any Docker based workflow such as Codefresh.

For the `KUBE_CONTEXT` environment variable just use the name of your cluster as found in the Codefresh Kubernetes dashboard. For the rest of the arguments you need to define them as parameters in your [codefresh.yml](example/codefresh.yml) file.

```
 canaryDeploy:
    title: "Deploying new version ${{CF_SHORT_REVISION}}"
    image: codefreshplugins/k8s-canary:master
    environment:
      - WORKING_VOLUME=.
      - SERVICE_NAME=my-demo-app
      - DEPLOYMENT_NAME=my-demo-app
      - TRAFFIC_INCREMENT=20
      - NEW_VERSION=${{CF_SHORT_REVISION}}
      - SLEEP_SECONDS=40
      - NAMESPACE=canary
      - KUBE_CONTEXT=myDemoAKSCluster
```

The `CF_SHORT_REVISION` variable is offered by Codefresh and contains the git hash of the version that was just pushed. See all variables in the [official documentation](https://codefresh.io/docs/docs/codefresh-yaml/variables/)

## Dockerhub

The canary step is now deployed in dockerhub as well

https://hub.docker.com/r/codefresh/k8s-canary/


## Future work

Further improvements

* Make the script create an initial deployment/service if nothing is deployed in the kubernetes cluster
* Add more complex and configurable healthchecks

