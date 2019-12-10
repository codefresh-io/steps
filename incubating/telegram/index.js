const BotController = require('./bot/bot.controller');
const config = require('./config');

// a workaround for the unset vars substituted as ${{VAR}}
for (var arg in process.env) {
    if (process.env[arg].match(/^\${{.*}}$/g)) {
        process.env[arg]='';
    }
}

const userEnv = {
    images: process.env.TELEGRAM_IMAGES,
    text: process.env.TELEGRAM_MESSAGE,
};

const botController = new BotController(config.accessToken);

const main = async () => {
   var notifyBots = config.to.split(',')
        .map(async uid => {
            if (!userEnv.text) {
                if (!process.env.CF_COMMIT_URL) {
                    throw Error("If the telegram_message is empty, it is expected that pipeline is triggered by a git trigger");
                }
                await botController.sendStatus(uid, userEnv.images);
            }
            else {
                await botController.sendTemplateMessage(uid, userEnv.text, {
                    ...(userEnv.images ? { images: userEnv.images.split(',') } : {}),
                });
            }
        });
    return Promise.all(notifyBots);
};

main()
    .then(() => console.log('\x1b[32mMessage has been successfully sent\x1b[0m'))
    .catch(e => {
        console.log(`\x1b[31m${e}\x1b[0m`);
        process.exit(1);
    })
    .finally(() => botController.stopBot());
