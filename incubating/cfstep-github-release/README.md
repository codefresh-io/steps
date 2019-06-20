# GitHub release Codefresh Plugin

A quick plugin to cover specific use case: create releases in GitHub and upload files for them. The plugin also allows to do more complex actions overriding the command manually.

## Basic usage

This example creates a release and uploads files to it:

``` yaml
github_prerelease:
  image: codefreshplugins/cfstep-github-release
  environment:
    - GITHUB_TOKEN=${{GITHUB_TOKEN}}
    - FILES=bin/app-*
    - PRERELEASE=true
```

## Advanced usage

If one wants to do more actions to manage releases than just to create them, it is possible to override the behaviour with custom commands:

``` yaml
github_release_modify:
  image: codefreshplugins/cfstep-github-release
  commands:
    - github-release edit --user $CF_REPO_OWNER --repo $CF_REPO_NAME --tag $CF_BRANCH_TAG_NORMALIZED --name "$CF_BRANCH_TAG_NORMALIZED"
    - github-release delete --user $CF_REPO_OWNER --repo $CF_REPO_NAME --tag $CF_BRANCH_TAG_NORMALIZED
    - github-release --help
```

More details about the paramaters and examples see [here](https://github.com/aktau/github-release)

## Environment Variables

- `GITHUB_TOKEN`: token for access to GitHub
- `CF_REPO_OWNER`: Codefresh provided variable containing repository owner name
- `CF_REPO_NAME`: Codefresh provided variable containing repository name
- `CF_BRANCH_TAG_NORMALIZED`: Codefresh provided variable containing tag name
- `CF_TARGET_BRANCH`: Codefresh provided variable containing target branch (default branch if not set)
- `PRERELEASE`: If true, this variable tells the plugin to create a pre-release
- `FILES`: A glob expression for the list of the files to be uploaded
