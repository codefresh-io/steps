FROM python:3.8.7-alpine3.12

# Gradle and jdk 8 are required for "jfrog rt gradle" commands. Version Note:
# The gradle package for alpine 3.12 (latest official version) is 5.6.4. If 
# you need a higher gradle version, switch from the official python base image
# (which uses an official version of alpine) to a base image with an "edge"
# version of alpine. For example, the alpine edge image "alpine:20201218" has
# a gradle package version of 6.7.1.

ENV CODEFRESH_CLI_VERSION=0.74.4
ENV JFROG_CLI_VERSION=1.43.2

RUN apk add --no-cache \
        bash \
        ca-certificates \
        docker \
        git \
        jq \
        nodejs \
        npm \
        openjdk8-jre \
        gradle && \
    pip install requests && \
    npm config set unsafe-perm true && \
    npm install codefresh@$CODEFRESH_CLI_VERSION -g && \
    wget -O /usr/local/bin/jfrog https://bintray.com/jfrog/jfrog-cli-go/download_file?file_path=$JFROG_CLI_VERSION%2Fjfrog-cli-linux-amd64%2Fjfrog && \
    chmod +x /usr/local/bin/jfrog

#COPY codefresh.py /codefresh.py

CMD [ "" ]