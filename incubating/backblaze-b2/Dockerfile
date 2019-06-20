FROM node:10.13.0-alpine

WORKDIR /root/backblaze-b2

RUN apk add --no-cache bash git openssh-client

COPY package.json ./

COPY yarn.lock ./

# install cf-api required binaries
RUN apk add --no-cache --virtual deps python make g++ krb5-dev && \
    yarn install --frozen-lockfile --production && \
    yarn cache clean && \
    apk del deps && \
    rm -rf /tmp/*

# copy app files
COPY . ./

# run application
CMD ["node", "/root/backblaze-b2/index.js"]
