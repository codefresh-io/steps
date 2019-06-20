const config = require('../config');
const request = require('request-promise');
const Handlebars = require('handlebars');

class PluginLogic {
    constructor() {
        this.sendRequest = this.sendRequest.bind(this);
    }

    /**
     * process variables from env as array, for example:
     * {HEADER_name1: val1, HEADER_name2: val2, otherVar: other val}
     * will be {name1: val1, name2: val2}
     * @param entityName
     * @param tplData
     * @return {{}}
     * @private
     */
    _resolveEnvArray(entityName, tplData) {
        const matchEntity = new RegExp(`^${entityName}_(.*)`);
        const entityFormat = new RegExp(`^${entityName}_`);
        return Object.entries(process.env)
            .filter(([key]) => matchEntity.test(key))
            .reduce((accumulator, [key, value]) => {
                const formattedKey = key.replace(entityFormat, '').trim();
                const templateValue = this._processTemplate(value, tplData).trim();
                return {
                    ...accumulator,
                    [formattedKey]: templateValue,
                };
            }, {});
    }

    /**
     * Resolve options for auth
     * @return {*}
     * @private
     */
    _resolveAuth() {
        if (config.token) {
            return {
                auth: {
                    bearer: config.token,
                },
            };
        }

        if (config.username && config.password) {
            return {
                auth: {
                    user: config.username,
                    pass: config.password,
                },
            };
        }

        return {};
    }

    /**
     * process text with data via handlebars
     * @param text
     * @param data
     * @return {string}
     * @private
     */
    _processTemplate(text, data) {
        const template = Handlebars.compile(text);
        return template(data);
    }


    /**
     * @param url
     * @param method
     * @param body
     * @param tplData
     * @return {Promise<void>}
     */
    sendRequest({ uri, method, body, tplData = {}, defaultHeaders = {} }) {
        return request({
            uri,
            method,
            body: this._processTemplate(body, tplData),
            qs: this._resolveEnvArray('QUERY', tplData),
            headers: Object.assign(defaultHeaders, this._resolveEnvArray('HEADER', tplData)),
            ...this._resolveAuth(),
        });
    }
}

module.exports = new PluginLogic();
