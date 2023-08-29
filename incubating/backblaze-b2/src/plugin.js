const _ = require('lodash');
const api = require('./backblaze-api');

const REQUIRED_VARAIBLES = [
    'APPLICATION_KEY_ID',
    'APPLICATION_KEY',
    'BUCKET_ID',
    'FILES'
];

// checking config
function getConfig() {
    const config = {
        appKeyId: process.env.APPLICATION_KEY_ID,
        appKey: process.env.APPLICATION_KEY,
        bucketId: process.env.BUCKET_ID,
    };

    REQUIRED_VARAIBLES.forEach((variable) => {
        if (!process.env[variable]) {
            console.error(`${variable} env variable should be present`);
            process.exit(1);
        }
    });

    return config;
}

function getBasicAuth(config) {
    const encoded = Buffer.from(`${config.appKeyId}:${config.appKey}`).toString('base64');
    return `Basic ${encoded}`;
}

async function runPlugin() {
    const config = getConfig();
    const authData = await api.auth(getBasicAuth(config));

    const files = process.env.FILES.split(',')

    return api.uploadFiles(authData, config.bucketId, files);
}

module.exports = runPlugin;
