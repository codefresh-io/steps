FROM quay.io/kubescape/kubescape-cli:v3.0.1

# Kubescape uses root privileges for writing the results to a file
USER root

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
