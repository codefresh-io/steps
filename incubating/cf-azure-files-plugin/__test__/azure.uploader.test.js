const { Aborter, ShareURL } = require('@azure/storage-file');
const AzureUploader = require('../src/azure.uploader');
const config = require('../src/config');

/**
 * To passed Upload file test create file data.txt within current directory
 */

describe('Azure Uploader', () => {
    describe('Correct path formatting', () => {
        it('relative path to file', () => {
            const service = new AzureUploader(config);

            const relativePath = 'data.txt';
            const formatedPath = service._formatPath(relativePath);

            const { cf: { volumePath, repoName } } = config;
  
            expect(formatedPath).toBe(`${volumePath}/${repoName}/${relativePath}`);
        });

        it('absolute path to file', () => {
            const service = new AzureUploader(config);

            const absolutePath = '/data.txt';
            const formatedPath = service._formatPath(absolutePath);
            expect(formatedPath).toBe(`/data.txt`);
        });
    });

    describe('Validation', () => {
        it('joi should throw an error if required env vars are missing', () => {
            const mocketObj = {
                SHARE_NAME: undefined,
                ACCOUNT_NAME: undefined,
                ACCOUNT_KEY: undefined,
                PATH_TO_FILE: undefined
            }
            expect(() => config.validateProperties(mocketObj)).toThrow();
        });
    });

    describe('Upload file', () => {
        const randomStr = () => Math.floor(Math.random() * 100000).toString();

        let azureUploader;
        let shareUrl;

        beforeEach(() => {
            const shareName = randomStr();
            const directory = randomStr();
            azureUploader = new AzureUploader({ ...config, shareName, directory });
            shareUrl = new ShareURL.fromServiceURL(azureUploader.serviceUrl, shareName);
        });

        afterEach(async (done) => {
            await shareUrl.delete(Aborter.none);
            done();
        });

        it('Upload data.txt', async () => {
            const fileUrl = await azureUploader.uploadFile(`${__dirname}/data.txt`);
            const result = await fileUrl.download(Aborter.none, 0);

            expect(result.originalResponse.readableStreamBody.statusCode).toBe(200);
        });
    });
});
