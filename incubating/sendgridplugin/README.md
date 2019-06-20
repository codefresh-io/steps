# Codefresh plugin for send e-mail letters

Codefresh plugin for send e-mails notification via SendGrid

## Main env variables
- `SENDGRID_APIKEY` - API key from SendGrid
- `SENDGRID_MAIL` - mail where the letter will be sent, you can use _comma_ divider to send on multiple mails (ex. `mail1@example.com, mail2@exmaple.com`)
- `SENDGRID_FROM` - from header of mail
- `SENDGRID_SUBJECT` - subject header of mail
- `SENDGRID_TYPE` - type of mail [build, message, custom]

## Mail types
### build
Info about current build
### message
Send simple message with text from `SENDGRID_MESSAGE`
### custom
Send message with custom template via [ejs](https://www.npmjs.com/package/ejs) provided `SENDGRID_TEMPLATE`

## Config for codefresh.yml
```
version: '1.0'
...
steps:
  ...
  TestMail:
    title: Test Mail
    image: 'codefreshplugins/sendgridplugin:latest'
  ...
...
```
