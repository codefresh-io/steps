const _ = require('lodash');

const VALIDATE_SCHEME = [
    { path: 'uploadOpts.host', required: true, type: 'string', varName: 'CF_SCP_HOST' },
    { path: 'uploadOpts.username', required: true, type: 'string', varName: 'CF_SCP_USER_NAME' },
    { path: 'uploadOpts.password', required: true, type: 'string', varName: 'CF_SCP_PASSWORD' },
    { path: 'uploadOpts.path', required: true, type: 'string', varName: 'CF_SCP_TARGET' },
    { path: 'uploadOpts.port', required: false, type: 'string', varName: 'CF_SCP_PORT' },
    { path: 'source', required: true, type: 'string', varName: 'CF_SCP_SOURCE' },
];

class Config {
    static getConfig() {
        const config =  {
            uploadOpts: {
                host: process.env.CF_SCP_HOST,
                username: process.env.CF_SCP_USER_NAME,
                password: process.env.CF_SCP_PASSWORD,
                path: process.env.CF_SCP_TARGET
            },
            source: process.env.CF_SCP_SOURCE,
        };

        if (process.env.CF_SCP_PORT) {
            config.uploadOpts.port = process.env.CF_SCP_PORT;
        }

        return config;
    }

    static validateConfig(config) {
        VALIDATE_SCHEME.forEach(({ path, required, type, varName }) => {
        	const value = _.get(config, path);

        	if (required && !value) {
        	   throw new Error(`Variable ${varName} is required`);
        	}

        	if (typeof value !== type) {
                throw new Error(`Variable ${varName} should be a ${type}`);
        	}
        });
    }
}

module.exports = Config;
