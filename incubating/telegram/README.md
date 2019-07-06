# Telegram notify plugin

Telegram plugin which gives the opportunity send any messages to users via bot.

## Using example

```yaml
version: '1.0'
...
steps:
  ...
  sendMessage:
    image: codefreshplugins/telegramnotifier
    environment:
      - TELEGRAM_TOKEN=${{TOKEN}}
      - TELEGRAM_TO=99999999
      - TELEGRAM_MESSAGE=Hello {{{userLink}}}, how are you
      - TELEGRAM_IMAGES=https://codefresh.io/docs/assets/brand/codefresh-social.png
```
Before using the plugin, make sure **you have started the bot** you've created for the notifications

An example of a more advanced notification message:
```
    #...
    environment:
      - "TELEGRAM_MESSAGE=buildTrigger: {{buildTrigger}}\nbuildInitiator: {{buildInitiator}}\nbuildId: {{buildId}}\nbuildTimestamp: {{buildTimestamp}}\nbuildUrl: {{buildUrl}}\nrepoOwner: {{repoOwner}}\nrepoName: {{repoName}}\nbranch: {{branch}}\nrevision: {{revision}}\ncommitAuthor: {{commitAuthor}}\ncommitUrl: {{commitUrl}}\ncommitMessage: {{commitMessage}}\nuserID: {{userID}}\nuserLink: {{{userLink}}}"

    # or you could write it in a YAML literal block:
    #...
    environment:
      - |-
        TELEGRAM_MESSAGE=
        buildTrigger: {{buildTrigger}}
        buildInitiator: {{buildInitiator}}
        buildId: {{buildId}}
        buildTimestamp: {{buildTimestamp}}
        buildUrl: {{buildUrl}}
        repoOwner: {{repoOwner}}
        repoName: {{repoName}}
        branch: {{branch}}
        revision: {{revision}}
        commitAuthor: {{commitAuthor}}
        commitUrl: {{commitUrl}}
        commitMessage: {{commitMessage}}
        userID: {{userID}}
        userLink: {{{userLink}}}
```
## Required variables

- `TELEGRAM_TOKEN` - token of your bot (cat get from [@BotFather](https://t.me/BotFather))
- `TELEGRAM_TO` - array of bot`s user id who will receive a message separated by comma (id you can retrieve from [@myidbot](https://t.me/myidbot))

## Optional variables

- `TELEGRAM_STATUS` - send info about current build, **if pass - all others variables will be ignore**
- `TELEGRAM_MESSAGE` - text of message which will be send to user, with [Handlebars.js](https://github.com/wycats/handlebars.js/), 
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
      - `{{userID}}` - id of current telegram user
      - `{{{userLink}}}` - link to current telegram user 
  
  - for text markup use Markdown
- `TELEGRAM_IMAGES` - array of link to images separated by comma, which will be attached to message
