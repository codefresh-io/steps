# Slack message sender

A plugin for easy sending messages to Slack from a Codefresh pipeline using channel name

## Usage
```
sendSlack:
    title: notifySlack
    type: 'slack-post-channel'
    arguments:
      SLACK_CHANNEL: "mychannel"   # or xxx@mycompany.com
      SLACK_TOKEN: "xxxx-xxxxx-xxxxx-xxxx"
      SLACK_MESSAGE: "this is my awesome message. Please <@U02M8S1BW7W> have a look
```
