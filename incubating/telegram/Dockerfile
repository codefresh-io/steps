FROM node:10.23.2-alpine

WORKDIR /app/

COPY package.json ./

COPY yarn.lock ./

RUN yarn install

COPY . ./

# below is needed to shut the deprecation warning messages
# raised in the node-telegram-bot-api module
ENV NTBA_FIX_350=1
ENV NTBA_FIX_319=1

CMD ["node", "/app/index.js"]
