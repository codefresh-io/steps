Example Use Case: 
- ArgoCD Synchronization of ApplicationSet deployed Applications 

Problem: 
- ArgoCD Sync step does not support running sync by injecting an ApplicationSet Manifest. 

Proposal: 
- Create a step that can parse ApplicationSet manifest and spin up separate child pipelines with ArgoCD sync steps for each. 

New Step: appset-runlist-creator 

Setup Parent/Child Pipelines: 

Parent: 
- GIT Triggers: 
- ApplicationSet file 
/applicationsets/helm-guestbook/helm-guestbook-applicationsets.yaml

```
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: helm-guestbook
spec:
  generators:
  - list:
      elements:
      - cluster: dev
        url: https://2A343DA625C5CD98C0D8616D5394DD00.gr7.us-west-2.eks.amazonaws.com
        namespace: development
      - cluster: stage
        url: https://E4AE0FC20FE62919F26F73A002E7D18E.gr7.us-west-2.eks.amazonaws.com
        namespace: staging
      - cluster: prod
        url: https://4590144362D24F48EF6C165BF1D32B3C.gr7.us-west-2.eks.amazonaws.com
        namespace: production
  template:
    metadata:
      name: '{{cluster}}-helm-guestbook'
    spec:
      project: default
      source:
        repoURL: https://gitea.dvb.sales-dev.codefresh.io/gitea_admin/helm-guestbook.git
        targetRevision: master
        path: .
      destination:
        server: '{{url}}'
        namespace: '{{namespace}}'
```

- Steps: 
Parent
- Clone ApplicationSet file’s repository 
- appset-runlist-creator, to generate runlist for dynamic pipeline step
- codefresh-run-dynamic, execute child pipelines for each Application 

Child: 
- check if argo application is out of sync 
- service-now, create Servicenow change request 
- approval, wait for Approval 
- argocd-sync, for each application 
- service-now, close Servicenow change request 

Parent Pipeline YAML
```
# More examples of Codefresh YAML can be found at
# https://codefresh.io/docs/docs/yaml-examples/examples/

version: "1.0"
# Stages can help you organize your steps in stages
stages:
  - "clone"
  - "create runlist"
  - "run children"

steps:
  Clone:
    title: "Cloning ApplicationSet repository"
    type: "git-clone"
    repo: "https://gitea.dvb.sales-dev.codefresh.io/gitea_admin/argocd-codefresh/"
    credentials:
      username: "gitea_admin"
      password: "${{GITEA_PASSWORD}}"
    revision: "master"
    stage: "clone"

  CreateApplicationSetRunlist:
    title: "Creating Runlist"
    type: "dustinvanbuskirk/appset-runlist-creator"
    arguments:
      APPLICATIONSET_FILE: "/codefresh/volume/argocd-codefresh/applicationsets/helm-guestbook/helm-guestbook-applicationset.yaml"
      PIPELINE: "ApplicationSets/helm-guestbook-child"
      RUNLIST_FILE: "/codefresh/volume/runlist.yaml"
      SHA: "990ce5f1141828e5590abadbe119ba579178262d"
      TRIGGER: "faux-trigger"
    stage: "create runlist"
      
  RunChildrenPipelines:
    title: "Running Children"
    type: "codefresh-run-dynamic"
    arguments:
      RUN_LIST_YAML_FILE: "/codefresh/volume/runlist.yaml"
    stage: "run children"

```

Child Pipeline YAML
```
# More examples of Codefresh YAML can be found at
# https://codefresh.io/docs/docs/yaml-examples/examples/

version: "1.0"
# Stages can help you organize your steps in stages
stages:
  - "sync application"

steps:
  SyncArgoCDApplication:
    title: "Syncing Application"
    type: "argocd-sync"
    arguments:
      context: "argocd"
      app_name: "${{cluster}}-helm-guestbook"
      sync: true
      wait_healthy: true
      rollback: true
    stage: "sync application"

```