FROM debian:stable-slim

WORKDIR /app

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y curl

RUN curl -fL https://getcli.jfrog.io | sh

ENV JFROG_CLI_OFFER_CONFIG false
ENV BINTRAY_LICENCES MIT

COPY run-jfrog-cli.sh /app

RUN chmod 777 "/app/run-jfrog-cli.sh"

CMD ["sh","-c", "/app/run-jfrog-cli.sh"]

