const types = {
  build: {
    message: `New build is ready!\nRepo: ${process.env.CF_REPO_NAME}\nBranch: ${process.env.CF_BRANCH_VERSION_NORMALIZED}\nDetail info: ${process.env.CF_BUILD_URL}`,
    env: ['CF_REPO_NAME', 'CF_BRANCH_VERSION_NORMALIZED', 'CF_BUILD_URL']
  },
  default: {
    message: `Text: ${process.env.TWILIO_MESSAGE}`,
    env: ['TWILIO_MESSAGE']
  },
}

module.exports = types