# cfstep-codecommit
Codefresh Step for Cloning an AWS CodeCommit Git repository

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| GIT_PASSWORD | null | string | Yes | AWS CodeCommit Git password |
| GIT_USER | null | string | Yes | AWS CodeCommit Git username |

``` yaml
  GitClone:
    image: codefreshplugins/cfstep-codecommit
    environment:
      - GIT_PASSWORD=########
      - GIT_USER=mygituser
```

Recommend putting GIT Credentials into a Shared Configuration

Note that you need to create a webhook from AWS to use this plugin - see more details in this blog post  https://docs.google.com/document/d/1mIVMLl9WbVHvBaHRduorkS3NhIE42KJRcONg8302ib8/edit?usp=sharing
