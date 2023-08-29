const config = require('./config');
const AzureUploader = require('./azure.uploader');

async function main() {
    const { credentials, shareName, directory, pathToFile, withTimeStamp } = config;

    const azureService = new AzureUploader({ credentials, shareName, directory });
    azureService.uploadFile(pathToFile, withTimeStamp);
}

main().catch(err => {
    console.error(err.stack);

    process.exit(1);
});