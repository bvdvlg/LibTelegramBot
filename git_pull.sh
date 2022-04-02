#!/bin/bash

rm /Users/bvdvlg/PycharmProjects/tgServer/key_storage/*.secret
git reset --hard
git pull origin main
for file in /Users/bvdvlg/PycharmProjects/tgServer/key_storage/*.gpg;do
len=${#file}
gpg --batch --output ${file::len-4}.secret --passphrase $1 --decrypt $file;done
rm /Users/bvdvlg/PycharmProjects/tgServer/key_storage/*.gpg
