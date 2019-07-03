module.exports = {
    url: process.env.WEBHOOK_URL,
    method: process.env.WEBHOOK_METHOD,
    username: process.env.WEBHOOK_USERNAME,
    password: process.env.WEBHOOK_PASSWORD,
    token: process.env.WEBHOOK_TOKEN,
    headers: process.env.WEBHOOK_HEADERS,
    query: process.env.WEBHOOK_QUERY,
    body: process.env.WEBHOOK_BODY,
};
