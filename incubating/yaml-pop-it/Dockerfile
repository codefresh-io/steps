FROM python:3.8.6-alpine3.12

RUN apk add linux-headers g++ python3-dev --no-cache
RUN pip install pyyaml requests in-place google-cloud-secret-manager --no-cache-dir

COPY templates/* /templates/
COPY lib/yaml-pop-it.py /yaml-pop-it.py