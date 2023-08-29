# Latest versions pinned in July 2021

FROM alpine:3.14.0

# Install Helm CLI
ENV HELM_VER=3.6.2
RUN cd /tmp && \
    wget https://get.helm.sh/helm-v${HELM_VER}-linux-amd64.tar.gz && \
    tar -zxvf helm-v${HELM_VER}-linux-amd64.tar.gz && \
    chmod +x linux-amd64/helm && \
    mv linux-amd64/helm /usr/local/bin/ && \
    rm -rf linux-amd64 && \
    rm helm-v${HELM_VER}-linux-amd64.tar.gz

# Install helm-push plugin, which includes cm:// protocol and token auth
RUN apk update && apk add git=2.32.0-r0
RUN helm plugin install https://github.com/chartmuseum/helm-push.git --version 0.9.0

COPY ./query.sh /query.sh

CMD ["/bin/sh"]