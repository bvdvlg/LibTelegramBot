#!/bin/bash

rm key_storage/*.secret
git reset --hard
git pull origin main
for file in key_storage/*.gpg;do
len=${#file}
gpg --batch --output ${file::len-4}.secret --passphrase $1 --decrypt $file;done
rm key_storage/*.gpg
