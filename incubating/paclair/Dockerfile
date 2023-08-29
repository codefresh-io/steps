FROM python:3.6.4-alpine3.7

ENV LANG C.UTF-8

ARG PACLAIR_VERSION=3.2.0

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git \
        nodejs && \
    pip install --no-cache-dir paclair==$PACLAIR_VERSION boto3 jinja2

RUN npm config set unsafe-perm true && \
    npm install codefresh -g

COPY script/paclair.py /paclair.py
COPY clair_config/paclair.conf.j2 /paclair.conf.j2

ENTRYPOINT ["python", "/paclair.py"]
CMD ["scan"]
