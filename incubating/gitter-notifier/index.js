const Controller = require('./plugin/controller');

const controller = new Controller();

controller.sendNotify()
    .then(console.log);
