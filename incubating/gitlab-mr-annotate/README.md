# Annotate GitLab Merge requests

The plugin allows for easy applying labels to GitLab merge requests from a Codefresh pipeline

## Basic usage 

```
AnnotateMR:
  image: codefreshplugins/gitlab-mr-annotate
  environment:
    - GIT_CONTEXT=my_gitlab_context_name
    - LABELS=my_label1,my_label2,my_label_n
```
## Environment variables

| Name             | Description                                                                                   | Default value                    |
|------------------|-----------------------------------------------------------------------------------------------|----------------------------------|
| GIT_CONTEXT      | The name of the git provider context you can see on the integrations page.                    | none                             |
| LABELS           | The comma separated list of labels you would like to apply to the merge request               | none                             |
| PROJECT_ID       | The ID of the GitLab project. Optional (the default value is formed from Codefresh variables) | $CF_REPO_OWNER%2F$CF_REPO_NAME   |
| MERGE_REQUEST_ID | The ID of the merge request.  Optional (the default value is formed from Codefresh variables) | $CF_PULL_REQUEST_ID              |