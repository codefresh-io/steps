ARG HELM_VERSION

FROM codefresh/cfstep-helm:${HELM_VERSION}

ARG HELM_VERSION
ARG HELMFILE_VERSION
ARG HELM_DIFF_VERSION
ARG HELM_SECRETS_VERSION

# Copy over modified command builders

COPY lib/EntrypointScriptBuilder.py /opt/lib/EntrypointScriptBuilder.py
COPY lib/Helm3CommandBuilder.py /opt/lib/Helm3CommandBuilder.py

# Install additional helm plugins

RUN helm plugin install https://github.com/databus23/helm-diff --version ${HELM_DIFF_VERSION} && \
    helm plugin install https://github.com/futuresimple/helm-secrets --version ${HELM_SECRETS_VERSION}

LABEL helm="${HELM_VERSION}"
LABEL helmdiff="${HELM_DIFF_VERSION}"
LABEL helmsecrets="${HELM_SECRETS_VERSION}"

ENTRYPOINT ["/opt/bin/release_chart"]