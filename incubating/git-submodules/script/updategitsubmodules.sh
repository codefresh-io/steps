#!/bin/sh
set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: \$GITHUB_TOKEN var is not set or empty"
    exit 1
fi

git config --global url.https://$GITHUB_TOKEN@github.com/.insteadOf git@github.com:

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
