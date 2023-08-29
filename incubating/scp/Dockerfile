FROM node:10.13.0-alpine

# Create app directory
WORKDIR /app/

COPY package.json ./

COPY yarn.lock ./

# install cf-api required binaries
RUN yarn install --frozen-lockfile --production

# copy app files
COPY . ./

# run application
CMD ["node", "/app/index.js"]
