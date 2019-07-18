#!/bin/bash

set -e

## CLONE_PATH doesn't include the repo-dir
## Repo-dir is $CLONE_PATH/$REPO_NAME
CLONE_PATH=${CLONE_PATH:-$(pwd)}
BRANCH=${BRANCH:-master}

if [[ ! -z "${REMOTE_URL}" ]]; then
  if [[ "$( echo ${REMOTE_URL:0:1} )" = "$( echo ${REMOTE_URL: -1} )" ]]; then
    export encaps=${REMOTE_URL:0:1}
    export REMOTE_URL="$(echo $REMOTE_URL | cut -d$encaps -f 2)"
  fi
else
  echo "REMOTE_URL not provided: $REMOTE_URL"
  exit 1
fi

if [[ ! -z "${SPLIT_CHAR}" ]]; then
  if [[ "${#SPLIT_CHAR}" > "1"  &&  "$( echo ${SPLIT_CHAR:0:1} )" = "$( echo ${SPLIT_CHAR: -1} )" ]]; then
    export encaps=${SPLIT_CHAR:0:1}
    export SPLIT_CHAR="$(echo $SPLIT_CHAR | cut -d$encaps -f 2)"
  fi
fi

if [[ ! -z "${BRANCH}" ]]; then
  if [[ "$( echo ${BRANCH:0:1} )" = "$( echo ${BRANCH: -1} )" ]]; then
    export encaps=${BRANCH:0:1}
    export BRANCH="$(echo $BRANCH | cut -d$encaps -f 2)"
  fi
fi

re="^(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$"

if [[ $REMOTE_URL =~ $re ]]; then
    protocol=${BASH_REMATCH[1]}
    separator=${BASH_REMATCH[2]}
    git_hostname=${BASH_REMATCH[3]}
    user=${BASH_REMATCH[4]}
    REPO_NAME=${BASH_REMATCH[5]}
else
  echo "Can't parse Remote URL: $REMOTE_URL"
  exit 1
fi

if [[ "$protocol" != "git" ]]; then
  echo "Not GIT+SSH formatted repository.: $REMOTE_URL"
  exit 1
fi

echo "GIT Hostname: $git_hostname"
echo "REPO: $REPO_NAME"

## Use SSH_KEY environment variable to create key file, if it does not exist
ssh_key_file="$HOME/.ssh/id_cfstep-gitclonerssh"
if [[ ! -f "$ssh_key_file" ]]; then 
  echo "Found $ssh_key_file file"
  rm -rf "$ssh_key_file"
fi

if [[ ! -z "${SSH_KEY}" ]]; then
  echo "SSH key passed through SSH_KEY environment variable: length check ${#SSH_KEY}"
  mkdir -p ~/.ssh
  if [[ ! -z "${SPLIT_CHAR}" ]]; then
    echo "SSH key split char: '${SPLIT_CHAR}'"
    echo "${SSH_KEY}" | tr \'"${SPLIT_CHAR}"\' '\n' | sed '/^$/d' > "$ssh_key_file"
  else
    echo "${SSH_KEY}" > "$ssh_key_file"
  fi
  chmod 600 "$ssh_key_file"
else
  echo "SSH_KEY variable not set"
  exit 1
fi

## Delete existing $CLONE_PATH/$REPO_NAME/ dir, to be able to clone there later
rm -rf $CLONE_PATH/$REPO_NAME/

## Be sure the path set by the user exists, so it can be used for cloning later
mkdir -p $CLONE_PATH

echo "Cloning $REMOTE_URL"
eval `ssh-agent -s`
ssh-keyscan $git_hostname >> ~/.ssh/known_hosts
ssh-add $ssh_key_file
git clone --bare -b staging --single-branch $REMOTE_URL $CLONE_PATH/$REPO_NAME
cd $CLONE_PATH/$REPO_NAME
find . --maxdepth 1 -exec mv {} .. \; && cd .. && rm -rf $REPO_NAME

## For the future: being aware of already cloned repo, intead of cloning it always:

# echo "\$CLONE_PATH var is $CLONE_PATH"
# Check if the cloned dir already exists from previous builds
# if [ -d "$CLONE_PATH/$REPO_NAME" ]; then
#   # Cloned dir already exists from previous builds so just fetch all the changes
#   echo "Preparing to update $REMOTE_URL"
#   cd $CLONE_PATH/$REPO_NAME

#   # Make sure the CLONE_PATH/REPO_NAME folder is a git folder
#   if git status &> /dev/null ; then
#     # Reset the remote URL because the embedded user token may have changed
#     git remote set-url origin $REPO_NAME

#     echo "Cleaning up the working directory"
#     git reset -q --hard
#     git clean -df
#     git gc
#     git_retry git remote prune origin

#     echo "Fetching the updates from origin"
#     ssh-agent bash -c "ssh-add $ssh_key_file; git_retry git fetch --tags"

#     if [ "$BRANCH" != "master" ]; then
#       git checkout $BRANCH && git branch && git status
#     fi
#   else
#     # The folder already exists but it is not a git repository
#     # Clean folder and clone a fresh copy on current directory
#     cd ..
#     rm -rf $CLONE_PATH/$REPO_NAME
#     echo "cloning $REPO_NAME"
#     ssh-agent bash -c "ssh-add $ssh_key_file; git clone $REMOTE_URL $CLONE_PATH"
#     git_retry git clone $REPO $CLONE_PATH/$REPO_NAME
#     cd $CLONE_PATH/$REPO_NAME

#     if [ "$BRANCH" != "master" ]; then
#       git checkout $BRANCH && git branch && git status
#     fi
#   fi
# else
#   mkdir -p $CLONE_PATH
#   # Clone a fresh copy
#   echo "Cloning $REMOTE_URL"
#   ssh-agent bash -c "ssh-add $ssh_key_file; git clone $REMOTE_URL $CLONE_PATH"
#   cd $CLONE_PATH

#   if [ "$BRANCH" != "master" ]; then
#     git checkout $BRANCH && git branch && git status
#   fi
# fi



