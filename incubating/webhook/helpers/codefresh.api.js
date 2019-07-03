const request = require('request-promise');

class Codefresh {
    /**
     *
     * @return {{build: {trigger: *, initiator: *, id: *, timestamp: *, url: *}, repo: {owner: *, name: *}, commit: {author: *, url: *, message: *}, revision: *, branch: *, apiKey: *}}
     */
    get info() {
        return {
            build: {
                trigger: process.env.CF_BUILD_TRIGGER,
                initiator: process.env.CF_BUILD_INITIATOR,
                id: process.env.CF_BUILD_ID,
                timestamp: process.env.CF_BUILD_TIMESTAMP,
                url: process.env.CF_BUILD_URL,
            },
            repo: {
                owner: process.env.CF_REPO_OWNER,
                name: process.env.CF_REPO_NAME,
            },
            commit: {
                author: process.env.CF_COMMIT_AUTHOR,
                url: process.env.CF_COMMIT_URL,
                message: process.env.CF_COMMIT_MESSAGE,
            },
            revision: process.env.CF_REVISION,
            branch: process.env.CF_BRANCH_TAG_NORMALIZED,
            apiKey: process.env.CF_API_KEY,
        };
    }

    async buildFailureCauses(buildId, token) {
        console.log(token, buildId);
        const data = await request({
            uri: `https://g.codefresh.io/api/workflow/${buildId}/context-revision`,
            method: 'GET',
            headers: {
                'authorization': token,
            },
            json: true,
        });

        return Object.entries(data.pop().context.stepsMetadata)
            .filter(([, stepInfo]) => stepInfo.status === 'failure')
            .map(([step]) => step);
    }
}

module.exports = new Codefresh();
