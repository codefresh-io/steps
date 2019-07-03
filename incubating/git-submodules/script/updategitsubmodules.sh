#!/bin/sh

if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: \$GITHUB_TOKEN var is not set or empty"
    exit
fi

mkdir ~/.ssh
ssh-keyscan github.com > ~/.ssh/known_hosts
sed -i 's/git@/https:\/\//' .gitmodules || exit
sed -i 's/ssh:\/\///' .gitmodules
sed -i 's/github.com:/github.com\//' .gitmodules
sed -i "s/https:\/\/github.com/https:\/\/$GITHUB_TOKEN@github.com/" .gitmodules

if [ "$CF_SUBMODULE_SYNC" = "true" ]; then
  echo "\$CF_SUBMODULE_SYNC var is set to 'true'. Syncing submodules"
  echo "git submodule sync"
  git submodule sync
fi

SUBMODULE_UPDATE_RECURSIVE_FLAG=""
if [ "$CF_SUBMODULE_UPDATE_RECURSIVE" = "true" ]; then
  echo "\$CF_SUBMODULE_UPDATE_RECURSIVE var is set to 'true'. Submodules will be recursively updated"
  SUBMODULE_UPDATE_RECURSIVE_FLAG=--recursive
fi

echo "Updating git submodules"
echo "git submodule update --init $SUBMODULE_UPDATE_RECURSIVE_FLAG"
git submodule update --init $SUBMODULE_UPDATE_RECURSIVE_FLAG
echo "Git submodules were updated"