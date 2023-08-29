FROM golang:latest as builder
RUN mkdir -p /go/src/github.com/codefresh-io/slack-message-sender
WORKDIR /go/src/github.com/codefresh-io/slack-message-sender
COPY . .
RUN "./hack/BUILD.sh"


FROM alpine:3.6

RUN apk add --no-cache ca-certificates

COPY --from=builder /go/src/github.com/codefresh-io/slack-message-sender/dist/bin/slack-message-sender /usr/bin/slack-message-sender
ENV PATH $PATH:/usr/bin/slack-message-sender
ENTRYPOINT ["slack-message-sender"]

CMD ["--help"]