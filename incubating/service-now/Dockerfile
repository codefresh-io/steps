FROM python:3.13.1-slim-bookworm
RUN pip3 install requests

COPY lib/snow.py /snow/snow.py
ENTRYPOINT [ "python3", "/snow/snow.py" ]
