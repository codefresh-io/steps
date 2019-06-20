FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

COPY packages/twistcli /usr/local/bin/twistcli

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        docker \
        git \
        nodejs && \
    pip install requests && \
    npm install codefresh -g && \
    chmod +x /usr/local/bin/twistcli

COPY script/twistlock-cli.py /twistlock-cli.py

CMD [""]
