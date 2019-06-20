const rp = require('request-promise');
const Promise = require('bluebird');
const fs = require('fs');
const util = require('util');
const crypto = require('crypto');

const BASE_URL = 'https://api.backblazeb2.com';
const AUTH_URL = '/b2api/v2/b2_authorize_account';
const GET_UPLOAD_URL = '/b2api/v2/b2_get_upload_url';

async function auth(authValue) {
    const response = await rp({
        uri: `${BASE_URL}${AUTH_URL}`,
        headers: {
            Authorization: authValue,
        },
        json: true,
    });
    return {
        apiUrl: response.apiUrl,
        authorizationToken: response.authorizationToken,
    };
}

function getUploadUrl({ authorizationToken, apiUrl }, bucketId) {
    return rp({
        uri: `${apiUrl}${GET_UPLOAD_URL}`,
        method: 'post',
        headers: {
            Authorization: authorizationToken,
        },
        body: {
            bucketId,
        },
        json: true,
    });
}

function getSha1(path) {
    const deferred = Promise.defer();
    const hash = crypto.createHash('sha1');
    const rs = fs.createReadStream(path);
    rs.on('error', e => deferred.reject(e));
    rs.on('data', chunk => hash.update(chunk));
    rs.on('end', () => deferred.resolve(hash.digest('hex')));
    return deferred.promise;
}

async function uploadFiles(authData, bucketId, files) {
    const result = [];
    await Promise.each(files, async (file) => {
        const uploadConfig = await getUploadUrl(authData, bucketId);
        const { authorizationToken, uploadUrl } = uploadConfig;

        const sha1 = await getSha1(file.path);
        const fileStat = util.promisify(fs.stat);
        const stat = await fileStat(file.path);
        const request = rp({
            uri: uploadUrl,
            method: 'post',
            headers: {
                Authorization: authorizationToken,
                'X-Bz-File-Name': file.name,
                'Content-Type': file.contentType || 'b2/x-auto',
                'Content-Length': stat.size,
                'X-Bz-Content-Sha1': sha1,
            },
            json: true,
        });
        await fs.createReadStream(file.path).pipe(request);
        result.push(request.response.body);
    });
    return result;
}

module.exports = {
    auth,
    uploadFiles,
};
