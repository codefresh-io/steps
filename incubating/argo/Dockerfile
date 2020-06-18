FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl jq

RUN curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/v1.5.5/argocd-linux-amd64
RUN chmod +x /usr/local/bin/argocd
