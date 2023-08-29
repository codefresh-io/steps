const client = require('scp2');
const { getConfig, validateConfig } = require('../config');

class SCP {
    static upload() {
        return new Promise((res, rej) => {
            const config = getConfig();
            validateConfig(config);

            client.scp(config.source, config.uploadOpts, (err) => {
                if (err) {
                    rej(err);
                }

                res(true);
            });
        });
    }
}

module.exports = SCP;
