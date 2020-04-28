FROM openjdk:buster

ENV LANG C.UTF-8

ARG CXCONSOLE_VERSION=2020.1.12

RUN apt-get update && \
    apt-get install -y \
      curl \
      unzip \
      python3

RUN curl -L https://download.checkmarx.com/9.0.0/Plugins/cli-$CXCONSOLE_VERSION.zip -o ./cx.zip && \
  unzip cx.zip -d opt/checkmarx && \
  rm -rf cx.zip && \
  mv "opt/checkmarx/CxConsolePlugin-$CXCONSOLE_VERSION" /opt/checkmarx/checkmarxcli && \
  chmod +x opt/checkmarx/checkmarxcli/runCxConsole.sh && \
  sed -i -e 's/\r$//' opt/checkmarx/checkmarxcli/runCxConsole.sh

COPY scripts /scripts

RUN	chmod +x /scripts

WORKDIR /scripts

ENTRYPOINT ["/usr/bin/python3"]
CMD [""]