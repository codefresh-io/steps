FROM codefresh/kube-helm:latest

RUN mkdir /app

COPY k8s-blue-green.sh /app

RUN chmod +x /app/k8s-blue-green.sh

CMD /app/k8s-blue-green.sh $SERVICE_NAME $DEPLOYMENT_NAME $NEW_VERSION true $HEALTH_SECONDS $NAMESPACE