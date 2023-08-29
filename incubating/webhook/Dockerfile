FROM node:16.20.1-bullseye-slim


#RUN apk add --no-cache bash git openssh-client

# Create app directory
WORKDIR /app/

COPY package.json ./

COPY yarn.lock ./

# install cf-api required binaries
RUN yarn install --frozen-lockfile --production

# copy app files
COPY . ./

RUN useradd -d /home/username -m -s /bin/bash codefresh

USER codefresh

# run application
CMD ["node", "/app/index.js"]
