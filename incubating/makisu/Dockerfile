ARG makisu_version

FROM gcr.io/makisu-project/makisu:v0.1.9 as makisu

FROM alpine:3.7

RUN apk -U add bash

COPY --from=makisu /makisu-internal/makisu /bin/makisu
COPY --from=makisu /makisu-internal/certs/cacerts.pem /makisu-internal/certs/cacerts.pem
COPY ./registry-conf.yml /makisu-internal/registry-conf.yml
COPY ./entrypoint.sh /entrypoint.sh

WORKDIR /makisu-context

SHELL ["/bin/bash"]
ENTRYPOINT /entrypoint.sh