# Gitter notify plugin

Gitter plugin which gives the opportunity send any messages to activity feed.

## Using example

```yaml
version: '1.0'
fail_fast: false
...
steps:
  ...
  sendMessage:
    image: codefreshplugins/gitternotifier
    environment:
      - GITTER_WEBHOOK=https://webhooks.gitter.im/e/123abc
```

## Required variables

- `GITTER_WEBHOOK` - webhook uri from  your [gitter](https://gitter.im) room integration

## Optional variables

**if you not provide this variables, plugin send info about build**

- `GITTER_STATUS`
  - **ok** - for info messages
  - **error** - for error messages (red icon, red text)
- `GITTER_MESSAGE` - text of custom message which will be send, with [Handlebars.js](https://github.com/wycats/handlebars.js/) 
  - available vars:
      - `{{buildTrigger}}` 
      - `{{buildInitiator}}`  
      - `{{buildId}}` 
      - `{{buildTimestamp}}`  
      - `{{buildUrl}}` 
      - `{{repoOwner}}`  
      - `{{repoName}}`  
      - `{{branch}}` 
      - `{{revision}}` 
      - `{{commitAuthor}}` 
      - `{{commitUrl}}` 
      - `{{commitMessage}}`  
  
  - for text markup use **Markdown**
