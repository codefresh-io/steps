module.exports = {
  envValid: (envs) => {
    for (let env of envs) {
      if (!process.env[env]) {
        throw Error(`Provide required env ${env} varible!`)
      }
    }
  }
}