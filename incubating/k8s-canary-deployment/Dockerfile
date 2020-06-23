FROM codefresh/node:10.15.3-alpine3.11


RUN apk add --update ca-certificates \
    && apk add bash curl jq \
    && apk add --no-cache git npm \
    && rm /var/cache/apk/* \
    && rm -rf /tmp/*

RUN npm install codefresh -g --unsafe-perm

# RUN curl -L "https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
#     && chmod +x /usr/local/bin/kubectl

RUN curl -L "https://storage.googleapis.com/kubernetes-release/release/v1.18.0/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

RUN mkdir /app

COPY k8s-canary-rollout.sh /app

RUN chmod +x /app/k8s-canary-rollout.sh

CMD /app/k8s-canary-rollout.sh $WORKING_VOLUME $SERVICE_NAME $DEPLOYMENT_NAME $TRAFFIC_INCREMENT $NAMESPACE $NEW_VERSION $SLEEP_SECONDS
