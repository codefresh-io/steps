# cfstep-aqua
Codefresh Step for Aqua Docker Image Scans

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| AQUA_HOST | null | string | Yes | Aqua Host URI including protocol ex. https://aqua.mydomain.com |
| AQUA_PASSWORD | null | string | Yes | Aqua Password |
| AQUA_USERNAME | null | string | Yes | Aqua Username |
| CF_ACCOUNT | CF_ACCOUNT | string | Yes | Auto pulled from pipeline also replaces REGISTRY if not provided |
| IMAGE | null | string | Yes | Docker Image Name |
| REGISTRY | null | string | No | Name of Codefresh Registry setup in Aqua |
| TAG | null | string | Yes | Docker Image Tag |

``` yaml
  AquaSecurityScan:
    image: codefresh/cfstep-aqua
    environment:
      - AQUA_HOST=http://0.0.0.0
      - AQUA_PASSWORD=########
      - AQUA_USERNAME=administator
      - IMAGE=example-voting-app/worker # Replace with your Docker image name
      - TAG=${{CF_BRANCH_TAG_NORMALIZED}}-${{CF_SHORT_REVISION}} # Replace with your Docker image tag
```

Recommend putting Aqua Credentials into a Shared Configuration