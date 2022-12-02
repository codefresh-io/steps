FROM python:3.10.0a7-slim
RUN pip3 install requests

COPY lib/snow.py /snow/snow.py
ENTRYPOINT [ "python3", "/snow/snow.py" ]
