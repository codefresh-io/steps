FROM amazon/aws-cli

RUN yum install -y tar gzip jq && \
    curl -sSL -o - https://github.com/codefresh-io/cli/releases/download/v0.82.5/codefresh-v0.82.5-linux-x64.tar.gz | tar zx codefresh && mv ./codefresh /usr/local/bin/codefresh && \
    yum remove -y tar gzip && \
    yum clean all && rm -rf /var/cache/yum

COPY ./src/start.sh /
