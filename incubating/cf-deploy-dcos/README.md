# cf-deploy-dcos
The repository contains code for `codefreshplugins/cf-deploy-dcos` image building. This image makes an application deployment on DC/OS cluster using application definition json file.
It takes application deployment template (deployment.tmpl) and generates application deployment json file substituting variables in the template with the the environment variables values then applies the application deployment json file to DC/OS cluster using DC/OS CLI command.


# Usage
In order to use the `codefreshplugins/cf-deploy-dcos` image we need to do the following:

1. Define environment variables in Codefresh pipeline.

- `DCOS_URL` **required** - DC/OS cluster URL
- `DCOS_CLUSTER_NAME` **required** - DC/OS cluster name
- `DCOS_CLUSTER_ID` **required** - DC/OS cluster ID
- `DCOS_DCOS_ACS_TOKEN` **required** - DC/OS cluster existing user's token (make it encrypted)
- `DCOS_SSL_VERIFY` default is true, if we want to bypass SSL certificate verification - set it to `false`
- `APP_ID` - application name
- `IMAGE_NAME` - application image name
- `IMAGE_TAG` - application image tag

2. Create deployment.tmpl and codefresh.yml files in an application repository at the root level.

```
codefresh.yml
---
version: '1.0'
steps:
  BuildingDockerImage:
    type: build
    image_name: applcation/image
    ...

  PushToRegistry:
    type: push
    candidate: ${{BuildingDockerImage}}
    ...

  DeployToDcos:
    image: codefreshplugins/cf-deploy-dcos:latest
    working_directory: ${{main_clone}}
    commands:
      - /cf-deploy-dcos deployment.tmpl
    environment:
      - DCOS_URL=${{DCOS_URL}}
      - DCOS_CLUSTER_NAME=${{DCOS_CLUSTER_NAME}}
      - DCOS_CLUSTER_ID=${{DCOS_CLUSTER_ID}}
      - DCOS_DCOS_ACS_TOKEN=${{DCOS_DCOS_ACS_TOKEN}}
      - DCOS_SSL_VERIFY=${{DCOS_SSL_VERIFY}}
      - APP_ID=${{APP_ID}}
      - IMAGE_NAME=${{IMAGE_NAME}}
      - IMAGE_TAG=${{IMAGE_TAG}}
```
We define freestyle step (DeployToDcos in the example above) and environment variables the same as in the Codefresh pipeline.

```
deployment.tmpl

{
  "id": "{{APP_ID}}",
  "instances": 1,
  "cpus": 0.1,
  "mem": 64,
  "container": {
    "type" : "DOCKER",
    "docker": {
      "image": "{{IMAGE_NAME}}:{{IMAGE_TAG}}",
      "forcePullImage": true,
      "privileged": false,
      "network": "BRIDGE",
      "portMappings": [
        { "hostPort": 80, "containerPort": 8081, "protocol": "tcp", "name": "http"}
      ]
    }
  },
   "acceptedResourceRoles": [
     "slave_public"
   ]
}
```
`APP_ID`, `IMAGE_NAME` and `IMAGE_TAG` variables are just examples. We can parametrise any value in application deployment template depending on our requirements.
But if we set some parameter `{{PARAMETER}}` in application deployment template we should ensure that this parameter is set both in Codefresh pipeline and in codefresh.yml freestyle step as well.

Notes: we can use already configured DC/OS CLI dcos command to get DC/OS cluster parameters.
Example:
```
dcos cluster list --attached --json

[
  {
    "attached": true,
    "cluster_id": "9d50f776-10d4-433c-9ae5-ebb01eaafbbc",
    "name": "dcos-master-ip-es-dcos-master-es-dcos",
    "url": "https://es-dcos-master.westeurope.cloudapp.azure.com",
    "version": "1.10.2"
  }
]
```
```
dcos config show core.dcos_acs_token

eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik9UQkVOakZFTWtWQ09VRTRPRVpGTlRNMFJrWXlRa015Tnprd1JrSkVRemRCTWpBM1FqYzVOZyJ9.eyJlbWFpbCI6ImV1Z2VuZUBjb2RlZnJlc2guaW8iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9kY29zLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExODA0MjgxODQ2NjI1NTk0NzkyOSIsImF1ZCI6IjN5RjVUT1N6ZGxJNDVRMXhzcHh6ZW9HQmU5Zk54bTltIiwiaWF0IjoxNTEyMTM3ODUyLCJleHAiOjE1MTI1Njk4NTJ9.Ckp3HcR0P31EaadOM1TXk1EwrgmsNM0Neem3U633g8wAt7xQXnYV9VymQz9cDMExzKQPTLmwHcIG7QDBrUO__eBznJRzThhvCfvS85N410WuaaYrjdYbKzkM9XiEeNpHNIa0JI5RfIMGX_4TGUuXvGkHXzZtGKxq40Zq5cMRgS71Seljzeor5SvxOU3Llwhlh4pgw3zRlDFVz7BoFNxOV19RpKxVZPrklM7tjEUn1mw6eEbFgL7oDnuXJEIMiNgYkgfTvz1tYWugtZA6GiWWnbRTqFRb0niaHE5EOOmsBx64BfMsK8OMEwAwflDVLSpmMd_GcFZYXz1twbzyn_qqmQ
```
