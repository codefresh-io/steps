FROM python:3.14.10-alpine3.23

ENV LANG C.UTF-8

ARG PYMSTEAMS_VERSION=0.1.9

RUN apk update && \
    apk upgrade --no-cache && \
    pip install --no-cache-dir \
        pymsteams==$PYMSTEAMS_VERSION \
        "certifi>=2026.10.19"

# pymsteams-workflow is vendored locally (see script/pymsteams_workflow.py) because
# the PyPI package installs under the module name "pymsteams" and collides with the
# legacy webhook client above.
COPY script/pymsteams-notifier.py /pymsteams-notifier.py
COPY script/pymsteams_workflow.py /pymsteams_workflow.py

ENTRYPOINT ["python", "/pymsteams-notifier.py"]
