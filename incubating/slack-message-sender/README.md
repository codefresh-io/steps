# Slack message sender

A plugin for easy sending messages to Slack from a Codefresh pipeline

## Usage
```
sendSlack:
    title: notifySlack
    image: 'codefreshplugins/slack-message-sender:0.1'
    commands:
      - slack-message-sender send --webhook-url https://my-webhook-url --message "My message"
```
## Run locally
`go get codefresh-io/slack-message-sender`
`slack-message-sender send --help`
```
NAME:
   slack-message-sender send -

USAGE:
   slack-message-sender send [command options] [arguments...]

DESCRIPTION:
   Send message to slack channel using webhook

OPTIONS:
   --webhook-url value         [$WEBHOOK_URL]
   --verbose, -v               [$DEBUG]
   --message value, -m value   [$SLACK_MESSAGE]

```
