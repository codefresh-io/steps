FROM python:3.9.1-alpine3.13

RUN pip install --no-cache-dir semver

COPY script/. /

ENTRYPOINT ["python", "/semversioner.py"]
