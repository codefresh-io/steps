FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    pip install --no-cache-dir requests

COPY script/bitbucket-buildstatus-notifier.py /bitbucket-buildstatus-notifier.py

ENTRYPOINT ["python", "/bitbucket-buildstatus-notifier.py"]