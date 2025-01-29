# gitops-argocd-sync

Syncs Argo CD apps managed by our GitOps Runtimes using Codefresh API

##  Installation 

* `pip3 install -r requirements.txt`

## Run

* `python3 argocd_sync.py`

## Supported parameters
| Name           | Description                                                                               | Optional | Default value                               |
|:---------------|:------------------------------------------------------------------------------------------|:---------|:--------------------------------------------|
| RUNTIME        | The name of the GitOps Runtime managing the Argo CD Application                           | false    |                                             |
| APPLICATION    | The name of the Argo CD Application to be synced                                          | false    |                                             |
| APP_NAMESPACE  | The namespace of the Argo CD Application to be synced, supported from app-proxy v1.2600.1 | true     |                                             |
| ROLLBACK       | Initiate a rollback to the previous revision if the Sync and Wait does not become healthy | true     |                                             |
| WAIT_ROLLBACK  | Wait for the app to be healthy after a rollback. Forces ROLLBACK to true                  | true     |                                             |
| CA_BUNDLE      | A base64 encoded string that contain the complete CA Certificate Bundle                   | true     |                                             |
| INSECURE       | Allows the usage of a self-signed certificate in the chain to reach the API endpoint      | true     |                                             |
| WAIT_HEALTHY   | Wait for the app to be healthy                                                            | true     | false                                       |
| INTERVAL       | Interval in seconds to wait between checks                                                | true     | 10                                          |
| MAX_CHECKS     | Maximum numbers of checks to do (to avoid forever wait)                                   | true     | 10                                          |
| LOG_LEVEL      | Set the log level, e.g. 'debug', 'info', 'warn', 'error', 'critical' (default 'error')    | true     | error                                       |
| CF_URL         | Codefresh API URL                                                                         | true     | https://g.codefresh.io                      |
| CF_API_KEY     | Codefresh API token                                                                       | true     |                                             |
| CF_STEP_NAME   | Used in generating a link to the Apps Dashboard                                           | true     | STEP_NAME                                   |
| IMAGE_NAME     | Overwrites the image name                                                                 | true     | quay.io/codefreshplugins/gitops-argocd-sync |
| IMAGE_TAG      | Overwrites the tag                                                                        | true     | 1.4.4                                       |
