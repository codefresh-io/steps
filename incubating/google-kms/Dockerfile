FROM google/cloud-sdk:alpine

WORKDIR /kms

RUN apk -U add jq bash 
ENV PATH=${PATH}:/kms

COPY google-kms.sh ./kms


