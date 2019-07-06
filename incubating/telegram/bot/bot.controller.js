const TelegramBot = require('node-telegram-bot-api');
const CfInfo = require('./bot.data');
const handlebars = require('handlebars');

const BotLogic = require('./bot.logic');

class BotController {
    /**
     * init BotController
     * @param token
     */
    constructor(token) {
        this.bot = new TelegramBot(token, {
            polling: true,
        });

        this.sendStatus = this.sendStatus.bind(this);
        this.sendTemplateMessage = this.sendTemplateMessage.bind(this);
        this.stopBot = this.stopBot.bind(this);
    }

    /**
     * send message with info about build
     * @param uid
     * @return {Promise}
     */
    sendStatus(uid) {
        return this.bot.sendPhoto(uid, './buildBanner.png', {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: BotLogic.keyboardBuildLinks(),
            },
            caption: BotLogic.buildStatusMessage(),
        });
    }

    /**
     * Send message with handlebars template
     * @param uid
     * @param message
     * @param options
     * @param options.images
     * @return {Promise}
     */
    sendTemplateMessage(uid, message, options = {}) {
        message = message.replace(/\\n/g, '\n');
        const template = handlebars.compile(message);
        const text = template({
            ...CfInfo.buildInfo,
            userID: uid,
            userLink: `[${CfInfo.buildInfo.buildInitiator}](tg://user?id=${uid})`,
        });

        if (options.images) {
            if (options.images.length > 1) {
                let media = options.images.map(item => ({
                    type: 'photo',
                    media: item,
                }));
                media[0] = { ...media[0], caption: text, parse_mode: 'Markdown' };
                return this.bot.sendMediaGroup(uid, media);
            }
            else {
                return this.bot.sendPhoto(uid, options.images[0], {
                    parse_mode: 'Markdown',
                    caption: text,
                });
            }
        }
        else {
            return this.bot.sendMessage(uid, text, {
                parse_mode: 'Markdown',
            });
        }

    }

    /**
     * Stop Telegram bot (use for exit plugin)
     * @return {Promise}
     */
    stopBot() {
        return this.bot.stopPolling();
    }
}

module.exports = BotController;
