FROM alpine:3.7

ENV GITHUB_RELEASE_VERSION=v0.7.2

RUN apk add --no-cache openssl bash curl
RUN wget https://github.com/aktau/github-release/releases/download/${GITHUB_RELEASE_VERSION}/linux-amd64-github-release.tar.bz2 -O - \
  | tar -xjf - -C /tmp \
  && mv /tmp/bin/linux/amd64/github-release /usr/local/bin \
  && rm -rf /tmp/

WORKDIR /plugin
COPY run.sh run.sh

SHELL ["/bin/bash"]

CMD /plugin/run.sh