FROM golang:latest as builder
RUN mkdir -p /go/src/github.com/codefresh-io/slack-post-channel
WORKDIR /go/src/github.com/codefresh-io/slack-post-channel
COPY . .
RUN "./hack/BUILD.sh"


FROM alpine:3.6

RUN apk add --no-cache ca-certificates

COPY --from=builder /go/src/github.com/codefresh-io/slack-post-channel/dist/bin/slack-post-channel /usr/bin/slack-post-channel
ENV PATH $PATH:/usr/bin/slack-post-channel
ENTRYPOINT ["slack-post-channel"]

CMD ["--help"]
