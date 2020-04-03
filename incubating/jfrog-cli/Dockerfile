FROM python:3.8.2-alpine3.11

ENV CODEFRESH_CLI_VERSION=0.50.1
ENV JFROG_CLI_VERSION=1.35.3

RUN apk add --no-cache \
        bash \
        ca-certificates \
        docker \
        git \
        jq \
        nodejs \
        npm && \
    pip install requests && \
    npm config set unsafe-perm true && \
    npm install codefresh@$CODEFRESH_CLI_VERSION -g && \
    wget -O /usr/local/bin/jfrog https://bintray.com/jfrog/jfrog-cli-go/download_file?file_path=$JFROG_CLI_VERSION%2Fjfrog-cli-linux-386%2Fjfrog && \
    chmod +x /usr/local/bin/jfrog

#COPY codefresh.py /codefresh.py

CMD [ "" ]