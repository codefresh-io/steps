const moment = require('moment');
const emoji = require('node-emoji');
const CfInfo = require('./bot.data');

class BotLogic {
    static buildStatusMessage() {
        return `Dear _${CfInfo.buildInfo.buildInitiator}_, you have new build via _${CfInfo.buildInfo.buildTrigger}_\n\n` +
            `*Repository*: ${CfInfo.buildInfo.repoName}\n` +
            `*Author*: ${CfInfo.buildInfo.commitAuthor}\n` +
            `*Branch*: ${CfInfo.buildInfo.branch}\n` +
            `*Time*: ${moment.unix(CfInfo.buildInfo.buildTimestamp / 1000)
                .format('MMMM Do YYYY, h:mm:ss a')}\n` +
            `*Commit message*: ${CfInfo.buildInfo.commitMessage}\n`;
    }

    static keyboardBuildLinks() {
        return [[{
            text: `${emoji.get('ribbon')} Build info`,
            url: CfInfo.buildInfo.buildUrl,
        }], [{
            text: `${emoji.get('key')} Commit info`,
            url: CfInfo.buildInfo.commitUrl,
        }]];
    }
}


module.exports = BotLogic;
