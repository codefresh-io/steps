# checkmarx-cli

Builds Docker image for Checkmarx CLI scans

### Build your own image:

 docker build -t <org>/<repo>:<tag> .


### Docker Usage:

 `docker run -it -s <cmarxDNS> -u <cmarxuser> -p "${{CMPASSWORD}}" -n "${{PROJECTNAME}}" -l GIT -r "${{GITURL}}" -b "refs/heads/${{CF_BRANCH}}" cfstep-checkmarx-cli:latest checkmarx.py`


### Usage in codefresh

See step.yaml
