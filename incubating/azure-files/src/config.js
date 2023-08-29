const Joi = require('joi');

const schema = Joi.object()
    .keys({
        ACCOUNT_NAME: Joi.string().required(),
        ACCOUNT_KEY: Joi.string().required(),
        SHARE_NAME: Joi.string().required(),
        PATH_TO_FILE: Joi.string().required(),
        DIRECTORY: Joi.string(),
        ADD_TIMESTAMP: Joi.bool()
    })
    .unknown(true);

const validateProperties = obj => {
    const result = Joi.validate(obj, schema);

    if (result.error !== null) {
        throw result.error;
    }
};

validateProperties(process.env);

const {
    ACCOUNT_NAME,
    ACCOUNT_KEY,
    SHARE_NAME,
    DIRECTORY,
    PATH_TO_FILE,
    ADD_TIMESTAMP,
    CF_VOLUME_PATH,
    CF_REPO_NAME
} = process.env;

module.exports = {
    credentials: {
        accName: ACCOUNT_NAME,
        accKey: ACCOUNT_KEY
    },
    shareName: SHARE_NAME,
    directory: DIRECTORY,
    pathToFile: PATH_TO_FILE,
    withTimeStamp: ADD_TIMESTAMP,
    cf: {
        volumePath: CF_VOLUME_PATH,
        repoName: CF_REPO_NAME
    }
};
