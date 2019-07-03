module.exports = {
  validateEnv: (envs) => {
    for (let env of envs) {
      if (!process.env[env]) {
        throw Error(`Provide required env ${env} varible!`)
      }
    }
  },
  htmlCharsDecode: (str) => {
    return str
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#039;/g, '\'')
  }
}