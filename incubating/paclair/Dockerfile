FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

ARG PACLAIR_VERSION

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git \
        nodejs && \
    pip install --no-cache-dir paclair==$PACLAIR_VERSION boto3 && \
    npm install codefresh -g

COPY script/paclair.py /paclair.py

ENTRYPOINT ["python", "/paclair.py"]
CMD ["scan"]