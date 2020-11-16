FROM python:3.8.5-alpine3.12

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        git && \
    pip install PyGithub GitPython pyyaml requests

COPY lib/yaml-editor.py /yaml-editor.py

COPY lib/git-committer.py /git-committer.py
