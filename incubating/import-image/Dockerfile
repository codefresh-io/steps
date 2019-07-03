FROM alexeiled/skopeo:develop

RUN apk add --no-cache bash curl ca-certificates jq || apk update && apk upgrade

ADD import.sh /
RUN chmod +x /import.sh

CMD ["/import.sh"]