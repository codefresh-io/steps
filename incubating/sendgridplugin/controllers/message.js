const ejs = require('ejs')
const helpers = require('../helpers')
module.exports = {
  getData() {
    helpers.validateEnv(['SENDGRID_MESSAGE'])
    return new Promise(resolve => {
      ejs.renderFile('./templates/message.ejs', {message: process.env.SENDGRID_MESSAGE}, (error, html) => {
        if (error) throw error

        resolve({html, txt: process.env.SENDGRID_MESSAGE})
      })
    })
  }
}