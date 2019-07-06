FROM node:10.13.0-alpine

WORKDIR /app/

COPY package.json ./

COPY yarn.lock ./

RUN yarn install

COPY . ./

ENV NTBA_FIX_319 1

CMD ["node", "/app/index.js"]
