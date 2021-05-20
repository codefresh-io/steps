FROM node:10.24.1-alpine3.11

# Versions pinned from May 2021
RUN apk update && apk add git=2.24.4-r0 python3=3.8.10-r0
RUN pip3 install pyyaml==5.4.1
RUN npm install -g codefresh@0.75.21

COPY codefresh-run-dynamic.py /

CMD ["/bin/sh"]