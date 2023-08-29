FROM python:3.9.6-alpine3.14

ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_DEFAULT_REGION=
ENV AWS_IAM_ROLE_ARN=
ENV SECRETS=

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY entrypoint.py entrypoint.py

CMD ["/app/entrypoint.py"]
