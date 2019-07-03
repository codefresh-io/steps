const sgMail = require('@sendgrid/mail')
const controllers = require('./controllers')
const helpers = require('./helpers')

helpers.validateEnv(['SENDGRID_APIKEY', 'SENDGRID_MAIL', 'SENDGRID_TYPE', 'SENDGRID_FROM', 'SENDGRID_SUBJECT'])

const API_KEY = process.env.SENDGRID_APIKEY
const MAIL = process.env.SENDGRID_MAIL.split(',').map(item => item.trim())
const subject = process.env.SENDGRID_SUBJECT
const from = process.env.SENDGRID_FROM


const send = async () => {
  let data = await controllers[process.env.SENDGRID_TYPE].getData()
  

  sgMail.setApiKey(API_KEY);
  const msg = {
    to: MAIL,
    from: helpers.htmlCharsDecode(from),
    subject: subject,
    text: data.txt,
    html: data.html
  };
  sgMail.send(msg);
}


send()
