const SCP = require('./SCP');

SCP.upload()
    .then(() => {
    	console.log('Successfully done. Exit');
        process.exit(0);
    })
    .catch((err) => {
        console.log('Error:');
    	console.log(err.message ? err.message : err);
    	process.exit(1);
    });
