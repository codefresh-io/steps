FROM quay.io/kubescape/kubescape:v3.0.3
WORKDIR /
RUN apk update && apk add bash

COPY entrypoint.sh .
ENTRYPOINT ["/entrypoint.sh"]
