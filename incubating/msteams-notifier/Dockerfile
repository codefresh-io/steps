FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

ARG PYMSTEAMS_VERSION

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git \
        nodejs && \
    pip install --no-cache-dir pymsteams==$PYMSTEAMS_VERSION

COPY script/pymsteams-notifier.py /pymsteams-notifier.py

ENTRYPOINT ["python", "/pymsteams-notifier.py"]
CMD ["scan"]