FROM node:10.13.0-alpine

WORKDIR /root/backblaze-b2

RUN apk add --no-cache bash git openssh-client

COPY package.json ./

COPY yarn.lock ./

RUN yarn install --frozen-lockfile --production && \
    yarn cache clean && \
    rm -rf /tmp/*

# copy app files
COPY index.js ./
COPY src/ src/

# run application
CMD ["node", "/root/backblaze-b2/index.js"]
