const pluginController = require('./plugin/plugin.controller');

pluginController.sendNotify()
    .then(console.log)
    .catch(console.error);
