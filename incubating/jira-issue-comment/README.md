# Codefresh Jira Issue Comment

This step will create a comment with build information on your Jira instance with the specified issue key. The Jira issue key can be set directly or by using a regex pattern against a source field. The inserted Jira comment id will be available within the same pipeline execution during later steps to update the initial comment.

## Prerequisites

- Create an [API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html) for Jira

## Important Notes
- Only populated data will be added to the comment

## Step arguments

Name|Required|Description
---|---|---
JIRA_BASE_URL | Yes | The base URL path to your Jira instance (please make sure it ends with /)
JIRA_USERNAME | Yes | The Jira username that you generated the API key with
JIRA_API_KEY | Yes | The generated Jira API Key
JIRA_ISSUE_SOURCE_FIELD | Yes | Jira Issue ID or Key
JIRA_ISSUE_SOURCE_FIELD_REGEX | No | Regex expression that will applied to the source field (see sample below)
BUILD_MESSAGE | No | Free form text that will be the first line of the comment
BUILD_STATUS | No | Free form text to display the current build status
JIRA_COMMENT_ID | No | Set a Jira comment ID to update an existing comment (Available as pipeline variable after step execution)
ADD_BRANCH_INFO | No | Add pipeline variable CF_BRANCH to the comment
ADD_COMMIT_INFO | No | Add pipeline variables CF_COMMIT_AUTHOR, CF_COMMIT_MESSAGE, and CF_COMMIT_URL to the comment
ADD_PR_INFO | No | Add pipeline variables CF_PULL_REQUEST_ACTION, CF_PULL_REQUEST_TARGET, CF_PULL_REQUEST_NUMBER, and CF_PULL_REQUEST_ID to the comment
VERBOSE | No | Enable verbose logging

### Jira Issue Regex Sample

JIRA_ISSUE_SOURCE_FIELD="branch/feature-SA-19/testing"
JIRA_ISSUE_SOURCE_FIELD_REGEX="[a-zA-Z]{2}-\d+"

This would set the Jira Issue Key to "SA-19". The example text in JIRA_ISSUE_SOURCE_FIELD can come from any variable you would like. In this example, the likely source of the branch information would be CF_BRANCH.

## Codefresh.yml

```yaml
version: '0.1.0'
steps:
  JiraIssueComment:
    title: Jira Issue Comment
    type: jira-issue-comment
    arguments:
      ANNOTATION_NAME: '${{CF_BRANCH}}'
```