const request = require('request-promise');
const Handlebars = require('handlebars');
const Codefresh = require('./codefresh');
const path = require('path');
const fs = require('fs');

class Controller {
    constructor() {
        this._sendMessage = this._sendMessage.bind(this);
        this._sendGitter = this._sendGitter.bind(this);
        this._sendStatus = this._sendStatus.bind(this);

        this._webhookUri = process.env.GITTER_WEBHOOK;
        this._status = process.env.GITTER_STATUS || 'ok';
        this._message = process.env.GITTER_MESSAGE;

        this.sendNotify = this.sendNotify.bind(this);
    }

    async sendNotify() {
        let commitUrl = process.env.CF_COMMIT_URL;
        if (!commitUrl) {
            throw Error(
            "The pipeline is supposed to be triggered by a git trigger " +
            "in case if there is no gitterMessage argument set by the user"
            );
        }   

        if (this._message) {
            return this._sendMessage(this._message);
        }

        return await this._sendStatus();
    }

    _sendGitter(message, type) {
        return request({
            method: 'POST',
            uri: this._webhookUri,
            json: true,
            body: {
                message: message,
                level: type,
            },
        });
    }

    _sendMessage(text) {
        const template = Handlebars.compile(text);
        const message = template(Codefresh.info);

        return this._sendGitter(message, this._status);
    }

    async _sendStatus() {
        const file = path.join(__dirname, '../messages/buildStatus.md');
        const data = fs.readFileSync(file, 'utf8');
        const template = Handlebars.compile(data);

        const buildCauses = await Codefresh.buildCauses(Codefresh.info.buildId, Codefresh.info.apiKey);

        const message = template({
            ...Codefresh.info,
            failure: !!buildCauses.length,
            buildCauses
        });

        return await this._sendGitter(message, buildCauses.length ? 'error' : 'info');
    }
}

module.exports = Controller;
