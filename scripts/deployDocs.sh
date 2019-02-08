#!/bin/bash

# package docs and deploy

DOC_PATH='./docs'
VERSION=`cat $DOC_PATH/source/conf.py | egrep 'release\s?=' | awk '{print $3}' | sed -e "s/^'//" -e "s/'$//"`
PROJECT_NAME=`cat $DOC_PATH/source/conf.py | egrep 'project\s?=' | awk '{print $3}' | sed -e "s/^'//" -e "s/'$//"`
SOURCE_FILES="$DOC_PATH/build/html/"
PACKAGE_NAME="docs_${PROJECT_NAME}_${VERSION}"
DEPLOY_FILENAME="${DOC_PATH}/${PACKAGE_NAME}.tar.gz"

DEPLOY_USER=docs_deploy

if [ ! -z "$1" ]; then
    DEPLOY_SERVER="$1"
fi

if [ ! -z "$2" ]; then
    DEPLOY_USER="$2"
fi

echo "building docs package $PACKAGE_NAME"

# install dev packages for doc build
pip install -e .[dev] -U tox-travis

# make the docs from source
make docs

# package into a tar.gz file for deployment
(cd "$SOURCE_FILES"; tar -czvf "../../../$DEPLOY_FILENAME" ./)

if [ ! -z "$DEPLOY_SERVER" ]; then
    DEPLOY_BUILD_URL="http://${DEPLOY_SERVER}/docs_build"

    echo "Deploying doc file to $DEPLOY_SERVER"
    openssl aes-256-cbc -K $encrypted_86d65e2fd543_key -iv $encrypted_86d65e2fd543_iv \
    -in docs/keys/dex-docs-deploy.enc \
    -out /tmp/dex-docs-deploy -d

    chmod 0600 /tmp/dex-docs-deploy
    scp -i /tmp/dex-docs-deploy "$DEPLOY_FILENAME" ${DEPLOY_USER}@${DEPLOY_SERVER}:
    rm /tmp/dex-docs-deploy

    echo "requesting docs rebuild at $DEPLOY_BUILD_URL"
    curl -H "Content-Type: application/json" -X POST -d '{"file":"$DEPLOY_FILENAME"}' "$DEPLOY_BUILD_URL"
fi