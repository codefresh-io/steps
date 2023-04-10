FROM amazon/aws-cli

RUN yum install -y tar gzip jq

RUN curl -sSL -o - https://github.com/codefresh-io/cli/releases/download/v0.82.5/codefresh-v0.82.5-linux-x64.tar.gz | tar zx codefresh && mv ./codefresh /usr/local/bin/codefresh

COPY ./src/start.sh ./