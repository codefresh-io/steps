const Controller = require('./plugin/controller');

// a workaround for the unset vars substituted as ${{VAR}}
for (var arg in process.env) {
    if (process.env[arg].includes("${{")) {
        process.env[arg]='';
    }
}

const controller = new Controller();

controller.sendNotify()
    .then(console.log)
    .catch((err)=>{
        console.log(`\x1b[31m\n${err.message}`);
        process.exit(1);
    });
