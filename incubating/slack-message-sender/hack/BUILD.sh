#!/bin/sh

echo "Building slack-message-sender"
CGO_ENABLED=0 go build -v -o "./dist/bin/slack-message-sender" *.go