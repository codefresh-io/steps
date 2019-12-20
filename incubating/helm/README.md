Custom Docker image to support clair image scanning from Codefresh pipeline

### Prerequisites:

Codefresh Subscription - https://codefresh.io/

### Documentation:

helm: https://helm.sh/docs/

### Full List of Arguments

Example `codefresh.yml` build is below with required Arguments in place.

| Arguments | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| kube_context | null | string | Yes | Kubernetes context to use (the name of the cluster as configured in Codefresh) |
| chart_name | null | string | Yes | Helm chart name to release (path to chart folder, or name of packaged chart) |
| release_name | null | string | Yes | Helm release name |
| action | null | string | No | The helm operation mode is set by the ACTION variable, where the value is install/auth/push |
| namespace | null | string | No | Target Kubernetes namespace |
| tiller_namespace | null | string | No | Kubernetes namespace where tiller is at |
| chart_version | null | string | No | Application chart version to install |
| helm_version | 2.9.1 | string | No | Version of cfstep-helm image(also helm-cli version). You can choose specific image at https://hub.docker.com/r/codefresh/cfstep-helm/tags |
| chart_repo_url | null | string | No | Helm chart repository URL (overriden by injected Helm repository context) |
| custom_value_files | null | array of strings | No | Values file to provide to Helm (as --values or -f). see usage information below |
| custom_values | null | array of strings | No | Variables to provide to Helm (as --set). see usage information below |
| cmd_ps | null | string | No | Variable to provide other Helm cli flags. For example: '--wait --timeout', etc |

### codefresh.yml

Codefresh Build Step to execute Clair scan.
All `${{var}}` variables must be put into Codefresh Build Parameters
codefresh.yml

```yaml
version: '1.0'
stages:
  - helm_deploy

steps:
  deploy_to_test_gke:
    type: helm
    stage: 'helm_deploy'
    arguments:
      action: install
      chart_name: my-chart
      release_name: prod
      kube_context: my-context
      tiller_namespace: kube-system
      namespace: kube-system
      helm_version: "2.14.3"
      chart_repo_url: https://my-chart.com/
      custom_values:
        - key1=val1
        - key2=val2
        - profiles.arr="{one,two,three}"
        - profiles.str="one\,two\,three"
      custom_value_files:
        - /path/to/values.yaml
      cmd_ps: --wait --timoeout 5
```
### Using as freestyle step

See documentation here: [https://codefresh.io/docs/docs/new-helm/using-helm-in-codefresh-pipeline/](https://codefresh.io/docs/docs/new-helm/using-helm-in-codefresh-pipeline/)
