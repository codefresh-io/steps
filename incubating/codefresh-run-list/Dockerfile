FROM node:10.24.1-alpine3.11

RUN apk update && apk add git python3 py3-pip
RUN npm install -g codefresh
RUN pip3 install pyyaml

CMD ["/bin/sh"]