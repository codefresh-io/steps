# Versions pinned from July 2021

FROM python:3.9.6-alpine3.14
RUN pip3 install pyyaml==5.4.1

# Install Helm CLI
ENV HELM_VER=3.6.2
RUN cd /tmp && \
    wget https://get.helm.sh/helm-v${HELM_VER}-linux-amd64.tar.gz && \
    tar -zxvf helm-v${HELM_VER}-linux-amd64.tar.gz && \
    chmod +x linux-amd64/helm && \
    mv linux-amd64/helm /usr/local/bin/ && \
    rm -rf linux-amd64 && \
    rm helm-v${HELM_VER}-linux-amd64.tar.gz

COPY update-chart.py /

CMD ["/bin/sh"]