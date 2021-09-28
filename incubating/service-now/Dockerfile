FROM python:3.10.0a7-alpine3.13
RUN pip3 install requests

COPY lib/snow.py /snow/snow.py
ENTRYPOINT [ "python3", "/snow/snow.py" ]
