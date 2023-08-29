FROM node:16-buster

RUN mkdir -p /app

WORKDIR /app

COPY package.json package-lock.json DeploymentMarker.js ./

RUN npm install

CMD [ "node" "/app/DeploymentMarker.js" ]
