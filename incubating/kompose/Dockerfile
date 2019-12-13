ARG HELM_VERSION=latest
FROM golang:1.9-alpine AS go

RUN apk add --no-cache git

# set kompose version
ARG KOMPOSE_VERSION=v1.5.0

# clone code and buid
RUN mkdir -p /go/src/github.com/kubernetes 
RUN git clone --branch ${KOMPOSE_VERSION} -- https://github.com/kubernetes/kompose.git /go/src/github.com/kubernetes/kompose
WORKDIR /go/src/github.com/kubernetes/kompose
RUN CGO_ENABLED=0 go build -o /kompose main.go

# helm and kubectl image
FROM dtzar/helm-kubectl:${HELM_VERSION} as helm

# main image
FROM alpine:3.10

# copy kompose
COPY --from=go /kompose /usr/local/bin/
# copy kubectl and helm
COPY --from=helm /usr/local/bin/helm /usr/bin/
COPY --from=helm /usr/local/bin/kubectl /usr/bin/

ADD bin/* /opt/bin/
RUN chmod +x /opt/bin/*

CMD ["/opt/bin/release_compose"]
