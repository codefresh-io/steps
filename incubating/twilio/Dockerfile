FROM node:10.23-alpine
WORKDIR /app/
COPY package.json ./
COPY yarn.lock ./
RUN yarn install
COPY . ./
CMD ["node", "/app/index.js"]
