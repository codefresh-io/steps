# cfstep-msteams-notifier
Codefresh Pipeline Step to Send Notification to Microsoft Teams

EXAMPLE CARD
![Microsoft Teams Example Card](/images/msteams_example_card.png)

YAML Step
``` yaml
  MSTeamsNotification:
    image: codefreshplugins/cfstep-msteams-notifier:latest
    environment:
      - MSTEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/37a4ea3d
```

This can be used for custom notifications of any type please see entire list of options on plugin.yml

PreReq:
Setting up a Microsoft Teams Channel Webhook Connector

https://docs.microsoft.com/en-us/microsoftteams/platform/concepts/connectors/connectors-using

Replace the MSTEAMS_WEBHOOK_URL value in the Basic YAML example with the URL provided after configuring the connection

This is the only required variable for the notification to send out on a pipeline execution.

TODO: Add links to Codefresh imagery for connector or card usage.

Want to send specific notifications based on the pipeline failing or succeeding?

Please see Codefresh Advanced Workflows which support workflow status conditionals.
https://codefresh.io/docs/docs/codefresh-yaml/advanced-workflows/#handling-error-conditions-in-a-pipeline

``` yaml
  MSTeamsNotificationError:
    image: codefreshplugins/cfstep-msteams-notifier:latest
    environment:
      - MSTEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/37a4ea3d...
      - CF_STATUS_MESSAGE=ERROR
      - MSTEAMS_ACTIVITY_IMAGE=error.png # Edit to reflect URL to custom Error image
      when:
        condition:
          all:
            myCondition: workflow.result == 'failure'
  MSTeamsNotificationSuccess:
    image: codefreshplugins/cfstep-msteams-notifier:latest
    environment:
      - MSTEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/37a4ea3d...
      - CF_STATUS_MESSAGE=SUCCESS
      - MSTEAMS_ACTIVITY_IMAGE=success.png # Edit to reflect URL to custom Success image
      when:
        condition:
          all:
            myCondition: workflow.result == 'success'
```