# Codefresh Kompose Plugin

Use Codefresh [Kompose](http://kompose.io) plugin to deploy or convert a Docker Compose file into Kubernetes resources.

## Usage

Set required and optional environment variable and add the following step to your Codefresh pipeline:

```yaml
---
version: '1.0'

steps:

  ...

  release_to_env:
    type: kompose
    arguments:
      KUBE_CONTEXT: "my_cluster"
      NAMESPACE: "default"

  ...

```

## Arguments

- **required** `KUBE_CONTEXT` - Kubernetes context to use
- **required** `NAMESPACE` - target Kubernetes namespace (default `default` namespace)
- `FILE` - Docker Compose file to deploy (default `docker-compose.yaml` file)
- `REPLICAS` - specify the number of replicas generated (default `1`)
- `VOLUMES` - volumes to be generated (`persistentVolumeClaim`|`emptyDir`) (default `persistentVolumeClaim`)
- `DRY_RUN` - do a "dry run" (print out) deployment (do not install anything, useful for Debug)
- `DEBUG` - print verbose install output


## Kubernetes Configuration

Add Kubernetes integration to Codefresh: `> Account Settings > Integration > Kubernetes`. From now on, you can use added Kubernetes cluster in Codefresh pipeline, addressing its context by the name you see in `Clusters` menu.

## Building Plugin

Use `docker build` command to build the plugin.
Two build arguments can be provided to override default `kubectl`, `helm` and `kompose` version:

- `HELM_VERSION` - default to `latest`
- `KOMPOSE_VERSION` - default to `v1.5.0`