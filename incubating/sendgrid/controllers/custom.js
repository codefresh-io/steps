const ejs = require('ejs')
const helpers = require('../helpers')
module.exports = {
  getData() {
    helpers.validateEnv(['SENDGRID_TEMPLATE'])
    const template = helpers.htmlCharsDecode(process.env.SENDGRID_TEMPLATE)
    
    return Promise.resolve({ html: ejs.render(template), txt: 'no txt format' })
  }
}