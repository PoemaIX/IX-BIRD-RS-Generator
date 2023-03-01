#!/bin/bash
set -x
set -e
cd /root/gitrs/KSKB-IX
git fetch --all --force
git reset --hard origin/main
python3 /root/arouteserver/syncRS.py
GIT_DIFF=$(git diff)
if  [[ $GIT_LAST_MSG == "sync members at"* ]] ; then
    echo "No diff, skip sync"
    exit 0
fi
DATE=$(date +'%Y-%m-%d %H:%M:%S')
GIT_LAST_MSG=$(git log -1 --pretty=%B)
git add -A
if ! git diff-index --quiet HEAD; then
  if  [[ $GIT_LAST_MSG == "sync members at"* ]] ;
  then
    #git commit -m "sync members at $DATE" --amend
    git commit -m "sync members at $DATE"
  else
    git commit -m "sync members at $DATE"
  fi
  git push -f
fi
