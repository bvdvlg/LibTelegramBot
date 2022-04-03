#!/bin/bash

COMMENT=$2 || "s"

for file in key_storage/*.secret;do
len=${#file}
gpg --batch --output ${file::len-7}.gpg --passphrase $1 --symmetric $file;done
rm key_storage/*.secret
git add templates helpers.py api/* tgServer/*.py tgServer/*.py manage.py git_push.sh git_pull.sh
git commit -m $COMMENT
for file in key_storage/*;do
echo $file;done
for file in key_storage/*.gpg;do
len=${#file}
gpg --batch --output ${file::len-4}.secret --passphrase $1 --decrypt $file;done
rm key_storage/*.gpg
git push --force
