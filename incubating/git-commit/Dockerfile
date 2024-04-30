# Moving to ubuntu instead of debian to solve high vulnerabilities
FROM ubuntu:jammy

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install git bash openssl busybox jq -y && \
    ln -s /bin/busybox /usr/bin/[[

# Add ssh record on which ssh key to use
COPY ./ssh/ /root/.ssh/

# USER nodeuser
RUN addgroup --gid 3000 nodegroup && \
    adduser --uid 3000 --ingroup nodegroup --shell /bin/sh --disabled-password nodeuser
USER nodeuser
