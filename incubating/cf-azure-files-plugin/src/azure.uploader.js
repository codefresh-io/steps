const path = require('path');
const Azure = require('@azure/storage-file');
const { cf } = require('./config');

const { SharedKeyCredential, ServiceURL, StorageURL, Aborter, ShareURL, DirectoryURL, FileURL, uploadFileToAzureFile } = Azure;

const rangeSize = 4 * 1024 * 1024;  // 4 MB
const parallelism = 20;

class AzureUploader {
    constructor({ credentials, shareName, directory }) {
        this.serviceUrl = this._createServiceUrl(credentials);
        this.shareName = shareName;
        this.pathToDir = directory;
    }

    async uploadFile(pathToFile, withTimeStamp) {
        this.shareUrl = await this._createShareUrl();
        this.dirUrl = await this._createDirectoryUrl(this.shareUrl, this.pathToDir);
        return this._upload(pathToFile, withTimeStamp);
    }

    _createServiceUrl({ accName, accKey }) {
        const sharedKeyCredential = new SharedKeyCredential(
            accName,
            accKey
        );

        const pipeline = StorageURL.newPipeline(sharedKeyCredential);

        return new ServiceURL(
            `https://${accName}.file.core.windows.net`,
            pipeline
        );
    }

    async _createShareUrl() {
        const shareUrl = ShareURL.fromServiceURL(this.serviceUrl, this.shareName);
        try {
            await shareUrl.create(Aborter.none);
            console.info('createShareUrl\t\t\t -> Share successfully created.');
        } catch (err) {
            if (err.body && err.body.Code === 'ShareAlreadyExists') {
                console.info('createShareUrl\t\t\t -> Share already created.');
            } else {
                throw err;
            }
        }

        return shareUrl;
    }

    async _createDirectoryUrl(shareUrl, dirName) {
        if (dirName) {
            let azureDirUrl;

            const splitedPath = dirName.split('/');
            const depth = splitedPath.length;

            const pathToDir = splitedPath.slice(0, -1).join('/');
            const targetDir = splitedPath.pop();

            if (depth > 1) {
                const azureParentDirUrl = await this._createDirectoryUrl(shareUrl, pathToDir)
                azureDirUrl = await this._createDir(azureParentDirUrl, targetDir);
            } else {
                azureDirUrl = await this._createDir(shareUrl, dirName);
            }

            return azureDirUrl;
        }
        console.info('\nDirectory url not specified, root by default.');
        return shareUrl;
    }

    async _createDir(azureUrl, dirName) {
        const directoryUrl = this._resolveDirUrl(azureUrl, dirName);

        try {
            await directoryUrl.create(Aborter.none);
            console.info(`createDirectoryUrl\t\t -> ${directoryUrl.url} Directory successfully created.`);
        } catch (err) {
            if (err.body && err.body.Code === 'ResourceAlreadyExists') {
                console.info(`createDirectoryUrl\t\t -> ${directoryUrl.url} Directory already created.`);
            } else {
                throw err;
            }
        }

        return directoryUrl;
    }

    _resolveDirUrl(azureUrl, dirName) {
        if (azureUrl instanceof Azure.ShareURL) {
            return DirectoryURL.fromShareURL(azureUrl, dirName);
        }
        return DirectoryURL.fromDirectoryURL(azureUrl, dirName)
    }

    async _upload(localPath, withTimeStamp) {
        let fileName = path.basename(localPath);
        const validLocalPath = this._formatPath(localPath);

        console.info(`\nLooking for ${path.resolve(validLocalPath)} ...\n`);

        if (withTimeStamp) {
            fileName = this._addTimeStampToFileName(fileName);
        }

        const fileUrl = FileURL.fromDirectoryURL(this.dirUrl, fileName);

        await uploadFileToAzureFile(Aborter.none, validLocalPath, fileUrl, {
            rangeSize,
            parallelism
        });
        console.info(`${fileName} successfully uploaded to ${fileUrl.url}`);

        return fileUrl;
    }

    _addTimeStampToFileName(fileName) {
        fileName = fileName.split('.');
        fileName.splice(fileName.length - 1, 0, Date.now());
        fileName = fileName.join('.');

        return fileName;
    }

    _formatPath(localPath = '/') {
        const { volumePath, repoName } = cf;

        const prefix = `${volumePath}/${repoName}/`;

        if (localPath[0] === '/') {
            return localPath;
        }

        return `${prefix}${localPath}`
    }
}

module.exports = AzureUploader;