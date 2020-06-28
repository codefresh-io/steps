FROM python:3.8.3-alpine3.12

ENV LANG C.UTF-8

RUN apk update && \
    apk upgrade && \
    pip install --no-cache-dir hvac

COPY script/. /

ENTRYPOINT ["python", "/vault.py"]
CMD [""]