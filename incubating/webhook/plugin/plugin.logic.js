const got = require('got');
const Handlebars = require('handlebars');
const config = require('../config');

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

    _resolveAuthHeaders() {
        if (config.token) {
            return {
                Authorization: `Bearer ${config.token}`,
            };
        }

        if (config.username && config.password) {
            const base64Payload = Buffer.from(`${config.username}:${config.password}`).toString('base64');
            return {
                Authorization: `Basic ${base64Payload}`,
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

    sendRequest({
        uri, method, body, tplData = {}, defaultHeaders = {},
    }) {
        return got({
            url: uri,
            method,
            body: this._processTemplate(body, tplData),
            searchParams: this._resolveEnvArray('QUERY', tplData),
            headers: Object.assign(
                defaultHeaders,
                this._resolveAuthHeaders(),
                this._resolveEnvArray('HEADER', tplData),
            ),
        });
    }
}

module.exports = new PluginLogic();
