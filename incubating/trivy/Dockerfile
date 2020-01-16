FROM aquasec/trivy:latest

ADD entrypoint.sh /usr/local/bin

RUN apk add --no-cache jq bash util-linux

ENTRYPOINT ["entrypoint.sh"]
