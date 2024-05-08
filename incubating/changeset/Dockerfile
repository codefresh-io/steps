FROM node:22.1-bullseye-slim

RUN apt-get update && apt-get install -y git grep bash

RUN mkdir -p /opt/changeset
COPY package.json  /opt/changeset
COPY yarn.lock     /opt/changeset

WORKDIR /opt/changeset
RUN yarn add -D @changesets/cli
