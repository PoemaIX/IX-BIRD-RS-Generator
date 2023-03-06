#!/bin/bash
set -x
set -e
cd /root/gitrs/KSKB-IX
git fetch --all --force
git reset --hard origin/main
/root/arouteserver/scripts/gen_ixpf.py | sed "s/fe80::/2404:f4c0:f70e:1980::/g" > /root/gitrs/KSKB-IX/static/files/ix-f.json
/root/arouteserver/scripts/gen_member_page.py
DATE=$(date +'%Y-%m-%d %H:%M:%S')
GIT_LAST_MSG=$(git log -1 --pretty=%B)
GIT_DIFF=$(git diff)
git add -A
if  [[ $GIT_LAST_MSG == "sync members at"* ]] ;
then
    git diff-index --quiet HEAD || git commit -m "sync members at $DATE" --amend
    #git commit -m "sync members at $DATE"
else
    git diff-index --quiet HEAD || git commit -m "sync members at $DATE"
fi
git push -f
