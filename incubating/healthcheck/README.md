# cfstep-healthcheck

Types:

`kubernetes_deployment` Check that Kubernetes deployment has all replicas available (Deployment Successful)

`kubernetes_statefulset` Check that Kubernetes statefulset has all replicas available (Deployment Successful)

`kubernetes_jobs` Check that Kubernetes job completed successfull if not return logs for containers from last executed pod.

`linkerd` Watch Prometheus metrics from Linkerd for given time confirming Success Rate remains higher than threshold configured.

`datadog-slo` Check that Datadog SLO is still matching expected SLA

If either of the above fail the step will fail accordingly

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| CLUSTER | null | string | No | Required for Kubernetes Type / Kubernetes Context Name |
| DEPLOY_TIMEOUT | 120 | integer | No | (seconds) Required for Kubernetes Type / Timeout for Deployment Completion |
| DEPLOY_WAIT | 5 | integer | No | (seconds) Between Deployment Checks |
| DEPLOYMENT | null | string | No | Kubernetes Deployment/Statefulset Name |
| JOB | null | string | No | Kubernetes Job Name |
| KUBE_CONFIG | null | string | Yes | Location of Kube Config file |
| METRIC_TIMEOUT | 120 | integer | No | (seconds) Required for Linkerd Type / Time to wait for Prometheus to return metrics |
| NAMESPACE | null | string | Yes | Kubernetes Namespace of Deployment |
| PROMETHEUS_URL | null | string | Yes | Prometheus URL including protocol and port |
| THRESHOLD | 1 | integer | No | Required for Linkerd Type / Percentage represented in 1 - .01 (100% - 1%) |
| TOTAL | 300 | integer | No | (seconds) Required for Linkerd Type / Total Time to Continue Testing |
| TYPES | null | string | Yes | Type of Tests to Run `;` delimited |
| WAIT | 15 | integer | No | (seconds) Wait between tests |
|DATADOG_API_KEY| null | string | No | Datadog API Key |
|DATADOG_APP_KEY| null | string | No | Datadog APP Key |
|DATADOG_SLO_LIST| null | string | No | Semicolon delimited string of SLO names |

Example Step Usage:

``` yaml
  CheckDeploymentHealth:
    title: Checking Deployment Health...
    image: dustinvanbuskirk/cfstep-healthcheck:alpha-statefulset
    environment:
      - TYPES=kubernetes_deployment,linkerd
      - CLUSTER=sales-demo@FirstKubernetes
      - DEPLOY_TIMEOUT=120
      - DEPLOYMENT=example-voting-app-vote
      - KUBE_CONFIG=/codefresh/volume/sensitive/.kube/config
      - METRIC_TIMEOUT=120
      - NAMESPACE=dustinvb-staging
      - PROMETHEUS_URL=http://10.59.254.185:9090
      - THRESHOLD=1
      - TOTAL=90
      - WAIT=15
```