#!/bin/bash

# removing old folders
rm -f ~/.my-credentials || true
rm -rf ${CF_REPO_NAME} || true

# authenticating using git credentials.helper
git config --global credential.helper 'store --file ~/.my-credentials'
echo https://${GIT_USER}:${GIT_PASSWORD}@git-codecommit.${REGION}.amazonaws.com >> ~/.my-credentials

# cloning the repo
git clone https://git-codecommit.${REGION}.amazonaws.com/v1/repos/${CF_REPO_NAME} /codefresh/volume/${CF_REPO_NAME}
cd ${CF_REPO_NAME}

# checking out branch
git checkout ${CF_BRANCH}
