# Telegram notify plugin

Telegram plugin which gives the opportunity send any messages to users via bot.

## Using example

An example below sends a notification with information about the current build. A few Codefresh variables values are automaticly added to the message. Requires a git trigger

```yaml
  ...
  sendMessage:
    type: telegram
    arguments:
      telegram_token: ${{TOKEN}}
      telegram_to:
        - 99999999
```
This example below shows how you can customize your notification message and attach to it images you'd like

```yaml
  ...
  sendMessage:
    type: telegram
    title: |-
      Sends a notification with your customized message
      and images to be attached
    arguments:
      telegram_token: ${{TOKEN}}
      telegram_to:
        - 99999999
      telegram_message: |-
        Hello, how are you? There was a build triggered by ${{CF_BUILD_INITIATOR}}
        You could see the build [here](${{CF_BUILD_URL}}) and the commit [here](${{CF_COMMIT_URL}})
      telegram_images:
        - https://codefresh.io/docs/assets/brand/codefresh-social.png
```

Before using the plugin, make sure **you have started the bot** you've created for the notifications

## Required arguments

- `telegram_token` - token of your bot, which you can get it from [@BotFather](https://t.me/BotFather))
- `telegram_to` - an array of bot`s user id who will receive a message (id you can retrieve from [@myidbot](https://t.me/myidbot))

## Optional variables

- `telegram_message` - allows you to customize the text of the notification message. You can use Markdown for text markup
- `telegram_images` - array of link to images separated by comma, which will be attached to message