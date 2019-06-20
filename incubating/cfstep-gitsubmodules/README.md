<br>
<img src="icon.jpg" alt="" width="210" height="110" /><br>

# Update git submodules
Plugin to update git submodules of an already cloned repo.

Dockerhub repo: https://hub.docker.com/r/codefresh/cfstep-gitsubmodules/tags

## Options
| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|--|--|--|--|--|
| GITHUB_TOKEN | null | string | Yes | GitHub Personal Token |
| CF_SUBMODULE_SYNC | null | boolean | No | If set to 'true', the step will perform 'git submodule sync' command |
| CF_SUBMODULE_UPDATE_RECURSIVE | null | boolean | No | If set to 'true', the step will perform 'git submodule update --init' command with '--recursive' option |

## Usage Example:

This  example updates submodule of a cloned repo.

The step assumes that the working directory is the cloned repo (which is the default working directory for any free style step)

```yaml
version: '1.0'
steps:
  updateSubmodules:
    image: codefreshplugins/cfstep-gitsubmodules
    environment:
      - GITHUB_TOKEN=<github_token>
      - CF_SUBMODULE_SYNC=<boolean to determine if modules should be synced>
      - CF_SUBMODULE_UPDATE_RECURSIVE=<boolean to determine if modules should be recursively updated>
```
