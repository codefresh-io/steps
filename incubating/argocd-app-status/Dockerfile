# stage 1 Build
# Bookworm is debian based
FROM    python:3.13.1-slim-bookworm AS builder
WORKDIR /app
COPY    requirements.txt requirements.txt
COPY    queries queries/
COPY    argocd_app_status.py argocd_app_status.py

RUN apt-get update && apt-get install -y binutils
RUN pip3 install -r requirements.txt
RUN pip3 install pyinstaller
RUN pyinstaller --strip --onefile argocd_app_status.py

# stage 2 : Prod
FROM    debian:bookworm-slim

# USER cfuser
RUN adduser cfuser --home /home/codefresh --shel /bin/sh
USER cfuser

WORKDIR /app
COPY    queries queries/
COPY    --from=builder /app/dist/argocd_app_status argocd_app_status
ENTRYPOINT ["/app/argocd_app_status"]
