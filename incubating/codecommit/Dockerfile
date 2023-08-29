FROM alpine:3.8

RUN apk add --no-cache git bash

COPY ./start.sh /run/start.sh
RUN chmod +x /run/start.sh

CMD ["/run/start.sh"]
