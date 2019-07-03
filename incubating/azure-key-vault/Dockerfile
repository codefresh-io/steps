FROM python:3.7.3-alpine3.8

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        gcc \
        libc-dev \
        libffi-dev \openssl-dev \
        python3-dev && \
    pip install \
        azure-common \
        azure-keyvault

COPY lib/azure-key-vault.py /azure-key-vault.py

ENTRYPOINT ["python", "/azure-key-vault.py"]