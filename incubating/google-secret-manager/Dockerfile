# syntax=docker/dockerfile:1

FROM python:3.11.0-alpine3.16

COPY src/ / 

RUN pip3 install -r requirements.txt

CMD [ "python3" , "get-secrets.py"]

