const BotController = require('./bot/bot.controller');
const config = require('./config');

const userEnv = {
    images: process.env.TELEGRAM_IMAGES,
    text: process.env.TELEGRAM_MESSAGE,
    onlyStatus: !!process.env.TELEGRAM_STATUS,
};

const botController = new BotController(config.accessToken);

const main = async () => {
    config.to.split(',')
        .map(async uid => {
            if (userEnv.onlyStatus) {
                await botController.sendStatus(uid);
            }
            else {
                await botController.sendTemplateMessage(uid, userEnv.text, {
                    ...(userEnv.images ? { images: userEnv.images.split(',') } : {}),
                });
            }
        });

};

main()
    .then(() => console.log('message successfully sanded'))
    .catch(e => {
        console.log(e);
    })
    .finally(() => botController.stopBot());
