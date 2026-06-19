FROM python:3.9.12-alpine3.15

ENV LANG C.UTF-8

ARG PYMSTEAMS_VERSION=0.1.9
ARG PYMSTEAMS_WORKFLOW_VERSION=1.0.5

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git \
        nodejs && \
    pip install --no-cache-dir pymsteams==$PYMSTEAMS_VERSION pymsteams-workflow==PYMSTEAMS_WORKFLOW_VERSION$

COPY script/pymsteams-notifier.py /pymsteams-notifier.py

ENTRYPOINT ["python", "/pymsteams-notifier.py"]
