const twilio = require('twilio')
const helpers = require('./helpers')
const types = require('./types')

helpers.envValid(['TWILIO_SID', 'TWILIO_TOKEN', 'TWILIO_PHONE_FROM', 'TWILIO_PHONE_TO'])

const client = twilio(process.env.TWILIO_SID, process.env.TWILIO_TOKEN)
const type = process.env.TWILIO_TYPE || 'default'

helpers.envValid(types[type].env)
message = types[type].message

client.messages
  .create({ from: process.env.TWILIO_PHONE_FROM, body: message, to: process.env.TWILIO_PHONE_TO })
  .then(message => console.log(message.sid))
  .catch(err => {
    throw err
  })
  .done()