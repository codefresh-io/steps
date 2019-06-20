FROM codefresh/kube-helm:master

RUN mkdir /app

COPY k8s-canary-rollout.sh /app

RUN chmod +x /app/k8s-canary-rollout.sh

CMD /app/k8s-canary-rollout.sh $WORKING_VOLUME $SERVICE_NAME $DEPLOYMENT_NAME $TRAFFIC_INCREMENT $NAMESPACE $NEW_VERSION $SLEEP_SECONDS
