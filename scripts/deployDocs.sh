#!/bin/bash

# package docs and deploy

DOC_PATH='./docs'
VERSION=`cat $DOC_PATH/source/conf.py | egrep 'release\s?=' | awk '{print $3}' | sed -e "s/^'//" -e "s/'$//"`
PROJECT_NAME=`cat $DOC_PATH/source/conf.py | egrep 'project\s?=' | awk '{print $3}' | sed -e "s/^'//" -e "s/'$//"`
SOURCE_FILES="$DOC_PATH/build/html/"
PACKAGE_NAME="docs_${PROJECT_NAME}_${VERSION}"


echo "building docs package $PACKAGE_NAME"

# install dev packages for doc build
pip install -e .[dev] -U tox-travis 

# make the docs from source
make docs

# package into a tar.gz file for deployment
tar -czvf "${DOC_PATH}/${PACKAGE_NAME}.tar.gz" "$SOURCE_FILES"

openssl aes-256-cbc -K $encrypted_e14c59e0af38_key -iv $encrypted_e14c59e0af38_iv \
-in docs/keys/dex-docs-deploy.enc \
-out /tmp/dex-docs-deploy -d

chmod 0600 /tmp/dex-docs-deploy
scp -i /tmp/dex-docs-deploy "${DOC_PATH}/${PACKAGE_NAME}.tar.gz" docs_deploy@shrimp.octet.services:
rm /tmp/dex-docs-deploy
