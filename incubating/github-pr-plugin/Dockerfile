FROM alpine:3.6

RUN apk add --no-cache curl bash

ADD ./run.sh /
RUN chmod +x /run.sh

CMD /run.sh
