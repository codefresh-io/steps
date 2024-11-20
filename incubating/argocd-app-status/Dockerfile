# stage 1 Build
FROM    python:3.13.0-slim-bookworm AS builder
WORKDIR /app
COPY    requirements.txt requirements.txt
COPY    queries queries/
COPY    argocd_app_status.py argocd_app_status.py

RUN     pip3 install -r requirements.txt
RUN     pip3 install pyinstaller
RUN     pyinstaller --onefile argocd_app_status.py

# stage 2 : Prod
FROM    alpine:3.20.3

# USER codefresh
RUN adduser -h /home/codefresh -D -s /usr/bin/bash codefresh
USER codefresh

WORKDIR /app
COPY    queries queries/
COPY    --from=builder dist/argocd_app_status argocd_app_status
ENTRYPOINT ["/app/argocd_app_status"]
