# Step to Fetch Secret from Google Secret Manager

PreReqs:

1. [Hybrid Codefresh Runner](https://codefresh.io/docs/docs/administration/codefresh-runner/) on GKE

1. GKE w/ [Workload Identity Enabled](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)

1. GKE w/ [Config Connector Enabled](https://cloud.google.com/config-connector/docs/how-to/getting-started)

1. Create IAM Policy Binding between GCP SA and GKE SA.

```
gcloud iam service-accounts add-iam-policy-binding <gcp-sa-name>@<gcp-project-name>.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:<gcp-project-name>.svc.id.goog[<runner-namespace>/default]"
```

1. Hybrid Codefresh Runner's Service Account `default` in the Runner namepsace must be properly annotated with a GSM Service Account that has access to Google Secret Manager to read the Secret.

Example of the annotation required.
```
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: <gcp-sa-name>@<gcp-project-name>.iam.gserviceaccount.com
  name: default
  namespace: codefresh
secrets:
- name: default-token
```