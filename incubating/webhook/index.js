const pluginController = require('./plugin/plugin.controller');

pluginController.sendNotify()
    .catch(console.error);
