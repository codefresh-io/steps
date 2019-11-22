# Gitter notify plugin

Gitter plugin which gives the opportunity send any messages to activity feed.

## Using example

An example below sends a notification with information about the current build. A few Codefresh variables values are automaticly added to the message. Requires a git trigger

```yaml
 ...
  sendMessage:
    type: gitter-notifier
    arguments:
      gitter_webhook: "https://webhooks.gitter.im/e/123abc"
```
The example below shows how you can customize your notification message and the gitter status.:

```yaml
  sendMessage:
    type: gitter-notifier
    arguments:
      gitter_webhook: "https://webhooks.gitter.im/e/123abc"
      gitter_message: |-
          Hello, how are you? There was a build triggered by ${{CF_BUILD_INITIATOR}}
          You could see the build [here](${{CF_BUILD_URL}}) and the commit [here](${{CF_COMMIT_URL}})
      gitter_status: "info"
```

## Required variables

- `gitter_webhook` - webhook uri from  your [gitter](https://gitter.im) room integration settings. Use "custom" integration type.

## Optional variables

**if you not provide this variables, plugin send info about build**

- `gitter_status`
  - **ok** - for info messages
  - **error** - for error messages (red icon, red text)
- `gitter_message` - text of custom message which will be send. You can substitute CF vars into it. For text markup use **Markdown**
