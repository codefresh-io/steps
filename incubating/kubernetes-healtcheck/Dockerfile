FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    apk add --no-cache curl \
        git \
        nodejs && \
    npm install codefresh -g && \
    pip install kubernetes \
        prometheus-http-client \
        requests

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.16.6/bin/linux/amd64/kubectl && \
    chmod u+x kubectl && mv kubectl /bin/kubectl

COPY lib/healthcheck.py /healthcheck.py

ENTRYPOINT ["python", "/healthcheck.py"]
CMD [""]