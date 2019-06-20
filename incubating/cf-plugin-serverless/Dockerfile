FROM node:10-alpine

# install helper packages
RUN apk add --no-cache curl ca-certificates

# set serverless versio
ARG SERVERLESS_VER
ENV SERVERLESS_VER ${SERVERLESS_VER:-1.28.0}

# install serverless
RUN echo "Building with serverless version: ${SERVERLESS_VER}"
RUN yarn global add serverless@${SERVERLESS_VER}