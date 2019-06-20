#!/usr/bin/env node

const npm   = require('npm-utils');
const _     = require('lodash');
const yargs = require('yargs');

const argv = yargs
    .command('$0', 'relative path for the directory', () => {}, (argv) => {
            dir = argv._[0];
            if(_.isUndefined(dir)){
                dir = '.';
            }
            try {
                process.chdir(dir)
            }
            catch (err) {
                onError("Publish to npm failed - Invalid path directory")
            }
            console.log('Current directory: ' + process.cwd());

            publishOptions = {};
            if(argv.tag)
                publishOptions.tag = argv.tag

            npm.setAuthToken()
                .then(npm.publish(publishOptions))
                .catch(onError);
    })
    .option('tag', {
        alias: 't',
        describe: 'optional tag to add to your npm package. npmjs.com default to \'latest\'',
    })
    .argv;

function onError (err) {
  console.error(err);
  process.exit(-1);
}
