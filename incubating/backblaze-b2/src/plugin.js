const _ = require('lodash');
const api = require('./backblaze-api');

const REQUIRED_VARAIBLES = [
    'APPLICATION_KEY_ID',
    'APPLICATION_KEY',
    'BUCKET_ID',
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

    // Parse files
    const vars = Object.entries(process.env).map(([key, value]) => {
        if (/^UPLOAD_FILE_/.test(key)) {
            const [path, name, contentType] = JSON.parse(value);
            return { path, name, contentType };
        }

        return null;
    });
    const files = _.compact(vars);

    if (!files.length) {
        console.error('At least one file should be specified for uploading. Set UPLOAD_FILE_1 variable.');
        process.exit(1);
    }

    return api.uploadFiles(authData, config.bucketId, files);
}

module.exports = runPlugin;
