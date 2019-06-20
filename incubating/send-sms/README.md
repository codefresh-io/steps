# Codefresh plugin for send SMS notification

Codefresh plugin for send SMS notification via Twilio

[![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/codefresh-inc/codefresh-io%2Ftwillio-plugin%2Ftwillio-plugin?branch=master&key=eyJhbGciOiJIUzI1NiJ9.NTY3MmQ4ZGViNjcyNGI2ZTM1OWFkZjYy.AN2wExsAsq7FseTbVxxWls8muNx_bBUnQWQVS8IgDTI&type=cf-2)]( https://g.codefresh.io/pipelines/twillio-plugin/builds?repoOwner=codefresh-io&repoName=twillio-plugin&serviceName=codefresh-io%2Ftwillio-plugin&filter=trigger:build~Build;branch:master;pipeline:5c1a73926ecec326b46fca2b~twillio-plugin)

## Main env variables
- `TWILIO_SID`
- `TWILIO_TOKEN`
- `TWILIO_PHONE_FROM`
- `TWILIO_PHONE_TO`
- `TWILIO_TYPE` - type of message [build, message, hello]

For **message** type you must provide `TWILIO_MESSAGE` env

## Config for codefresh.yml
```
version: '1.0'
...
steps:
  ...
  TestSMS:
    title: Test SMS
    image: codefreshplugins/twilioplugin:latest
  ...
...
```

