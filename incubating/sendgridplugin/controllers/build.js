const ejs = require('ejs')
const helpers = require('../helpers')

const data = [
  {
    name: 'Branch',
    val: process.env.CF_BRANCH,
  },
  {
    name: 'Author',
    val: process.env.CF_COMMIT_AUTHOR,
  },
  {
    name: 'Build ID',
    val: process.env.CF_BUILD_ID,
  },
  {
    name: 'Logs',
    val: process.env.CF_BUILD_URL
  },
  {
    name: 'Repository',
    val: process.env.CF_REPO_NAME
  }
]

module.exports = {
  getData() {
    helpers.validateEnv(['CF_BRANCH', 'CF_COMMIT_AUTHOR', 'CF_BUILD_ID', 'CF_BUILD_URL', 'CF_REPO_NAME'])
    return new Promise(resolve => {
      ejs.renderFile('./templates/build.ejs', {items: data}, (error, html) => {
        if (error) throw error

        resolve({html, txt: data.map(item => `${item.name}: ${item.val}`).join('\r\n\r\n')})
      })
    })
  }
}