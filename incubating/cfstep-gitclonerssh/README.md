# Clone repository via SSH
Plugin to clone git repositories via SSH.

Dockerhub repo: https://hub.docker.com/r/codefresh/cfstep-gitclonerssh

## Options
| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|--|--|--|--|--|
| REMOTE_URL | null | string | Yes | Reporitory SSH URL (e.g. `git@github.com:my-user/my-repo.git`) |
| BRANCH | master | string | No | Branch name to checkout (e.g. `master`) |
| SSH_KEY | null | string | Yes | Private SSH key to access the repository. To convert it to single line string, and set a value for this var you can execute: `cat ~/.ssh/my_ssh_key_file | tr '\n' ','`. This assumes that `SPLIT_CHAR` will be set to `,` |
| SPLIT_CHAR | null | string | Yes | Split character you’ve used to replace newline in SSH key (`SSH_KEY`). Recommendation: use `,` (comma character)|
| CLONE_PATH | working directory | string | No | Path where `git clone` is going to be executed. A "`repo-name`" directory will be created there|

## Usage Example:
This  example clones a private repo using a private SSH key.
This example assumes that `SSH_KEY` var is already saved as an encrypted-pipeline-var. And that `SPLIT_CHAR` has a value of ','.

```yaml
version: '1.0'
steps:
  clone_repo_via_ssh:
    image: codefresh/cfstep-gitclonerssh
    environment:
      - REMOTE_URL=git@github.com:my-user/my-repo.git
      - BRANCH=my-branch
      - SSH_KEY=${{SSH_KEY}}
      - SPLIT_CHAR=${{SPLIT_CHAR}}
      - CLONE_PATH=/codefresh/volume 
```
