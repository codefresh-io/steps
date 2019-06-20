const plugin = require('./src/plugin');

plugin()
    .then((response) => {
        console.log(`Backblaze B2 plugin executed succesfully. Files uploaded: ${response.length}`);

        if (response.length) {
            console.log(`accountId: ${response[0].accountId}`);
            console.log(`action: ${response[0].action}`);
            console.log(`bucketId: ${response[0].bucketId}\n`);

            response.forEach((file, index) => {
                console.log(`_file ${index + 1}_`);
                console.log(`contentType: ${file.contentType}`);
                console.log(`fileId: ${file.fileId}`);
                console.log(`fileName: ${file.fileName}`);
                console.log(`uploadTimestamp: ${file.uploadTimestamp}\n`);
            });
        }
    })
    .catch((e) => {
        console.error(e);
    });
