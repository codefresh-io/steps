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
    type: gitter-notifier
    arguments:
      gitter_webhook: "https://webhooks.gitter.im/e/123abc"
```

## Required variables

- `gitter_webhook` - webhook uri from  your [gitter](https://gitter.im) room integration settings. Use "custom" integration type.

## Optional variables

**if you not provide this variables, plugin send info about build**

- `gitter_status`
  - **ok** - for info messages
  - **error** - for error messages (red icon, red text)
- `gitter_message` - text of custom message which will be send, with [Handlebars.js](https://github.com/wycats/handlebars.js/) 
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
