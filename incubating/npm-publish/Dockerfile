FROM node:8.8.0-alpine

WORKDIR /publish

COPY package.json /publish

COPY npm-publish.js /publish

RUN ["npm", "install"]

ENTRYPOINT ["node","/publish/npm-publish.js"]


