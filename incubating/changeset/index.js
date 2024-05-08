import path from 'path'
import core from '@actions/core'
import github from '@actions/github'
import write from '@changesets/write'
import { createLogger } from '@generates/logger'
import dot from '@ianwalter/dot'
import execa from 'execa'
import { readPackageUpAsync } from 'read-pkg-up'

const logger = createLogger({ level: 'info', namespace: 'changeset-action' })
const types = ['major', 'minor', 'patch']
const ignoredFiles = ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']

async function run () {
  // Try to extract changeset data from the workflow context.
  logger.debug('Context', github.context)
  let {
    type,
    name,
    summary,
    token = process.env.INPUT_TOKEN
  } = github.context.payload.inputs || {}

  // Try to extract changeset data from the pull request label or workflow
  // input.
  const { labels = [], base, head } = github.context.payload?.pull_request || {}
  if (!type) {
    for (const label of labels) {
      const [ns, t] = label.name.split('.')
      if (ns === 'changeset' && types.includes(t)) {
        type = t
        break
      }
    }
  }

  if (types.includes(type)) {
    // Get the package name from the workflow input or try to determine it by
    // finding the nearest package.json to the first changed file.
    const releases = []
    if (name) {
      releases.push({ name, type })
    } else {
      // Get the list of changed files from GitHub.
      const octokit = github.getOctokit(token)
      const res = await octokit.rest.repos.compareCommits({
        base: base.sha,
        head: head.sha,
        owner: github.context.repo.owner,
        repo: github.context.repo.repo
      })

      logger.info('Files', res.data.files)

      for (const file of res.data.files) {
        if (!ignoredFiles.includes(file.filename)) {
          const cwd = path.resolve(path.dirname(file.filename))
          const { packageJson, ...pkg } = await readPackageUpAsync({ cwd })
          const hasPackage = releases.some(r => r.name === packageJson.name)
          if (!hasPackage) releases.push({ name: packageJson.name, type })
          logger.debug('File', { file, ...pkg, cwd, hasPackage })
        }
      }
    }

    // Get the changeset summary from the workflow input or from the title of
    // the pull request.
    summary = summary || dot.get(github.context, 'payload.pull_request.title')
    if (!summary) throw new Error('Changeset summary could not be determined')

    // Don't create a new changeset if it already exists.
    const opts = { reject: false }
    const { stdout } = await execa('grep', [summary, '-r', '.changeset'], opts)
    if (stdout) return logger.info('Found existing changeset:', stdout)

    // Create the changeset.
    const cwd = process.cwd()
    await write.default({ summary, releases }, cwd)
  } else {
    logger.info('Not adding changeset', { type, labels })
  }
}

run().catch(err => {
  logger.error(err)
  core.setFailed(err.message)
})
