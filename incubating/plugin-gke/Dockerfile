FROM google/cloud-sdk:227.0.0-alpine

ARG KUBECTL_VERSION="v1.12.3"
ENV KUBECTL_VERSION=$KUBECTL_VERSION

RUN curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && apk add jq --no-cache

ADD bin /usr/local/bin

CMD ["bash"]

