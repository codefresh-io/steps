FROM vault:1.0.1 AS vault

FROM alpine:3.8

RUN apk add --no-cache curl curl-dev jq bash

COPY --from=vault /bin/vault /usr/bin

ADD ./script.sh /script.sh
RUN chmod +x /script.sh

CMD ["/script.sh"]

