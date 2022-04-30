# Slack message sender

A plugin for easy sending messages to Slack from a Codefresh pipeline using channel name

## Usage
```
sendSlack:
    title: notifySlack
    type: 'slack-post-channel:0.0.1'
    arguments:
      SLACK_CHANNEL: "mychannel"
      SLACK_TOKEN: "xxxx-xxxxx-xxxxx-xxxx"
      SLACK_MESSAGE: "this is my awesome message"
```
