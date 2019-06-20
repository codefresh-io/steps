FROM node:8.8.0-alpine

WORKDIR .

COPY . .

RUN ["npm", "install"]

ENTRYPOINT ["node","npm-publish.js"]


