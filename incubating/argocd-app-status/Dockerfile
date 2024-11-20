# stage 1 Build
FROM    python:3.13.0-slim-bookworm AS builder
WORKDIR /app
COPY    requirements.txt requirements.txt
RUN     pip3 install -r requirements.txt
COPY    queries queries/
COPY    argocd_app_status.py argocd_app_status.py

RUN pip3 install pyinstaller
RUN pyinstaller --onefile argocd app_status.py

# stage 2 : Prod
FROM    scratch

# USER codefresh
RUN useradd -d /home/codefresh -m -s /usr/bin/bash codefresh
USER codefresh

WORKDIR /app
COPY    queries queries/
COPY    dist/argocd_app_status argocd_app_status
CMD     argocd_app_status
