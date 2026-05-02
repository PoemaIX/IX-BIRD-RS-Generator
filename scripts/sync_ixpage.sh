#!/bin/bash
set -x
set -e
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export PATH=$HOME/.local/bin:$PATH
. ~/.bashrc
eval "$(pyenv init - bash)"
pyenv install -s 3.11.5
cd /root/gitrs/KSKB-IX
git fetch --all --force
git reset --hard origin/main
/root/arouteserver/scripts/gen_ixpf.py | sed "s/fe80::/2404:f4c0:f70e:1980::/g" > /root/gitrs/KSKB-IX/static/files/ix-f.json
/root/arouteserver/scripts/gen_member_page.py

if git diff --quiet -- static/files/ix-f.json docs/members.md; then
  echo "No changes detected, skipping ixpage update"
  exit 0
fi

DATE=$(date +'%Y-%m-%d %H:%M:%S')

build_mkdocs=

while [ "$1" != "" ]; do
    case $1 in
        -b | --build )    build_mkdocs=1
                                ;;
    esac
    shift
done

if [ "$build_mkdocs" = "1" ]; then
  pipenv install
  export SOURCE_DATE_EPOCH=$(date -d "$(git -C /root/gitrs/KSKB-IX log -1 --pretty="format:%ci" docs)"  +"%s")
  pipenv run mkdocs build
  gzip -f -n -k site/sitemap.xml
fi

mkdir -p /tmp/ixpage_bak
cp -r site /tmp/ixpage_bak/ 2>/dev/null || true
pip3 install git-filter-repo
git filter-repo --invert-paths --path site/ --force
cp -r /tmp/ixpage_bak/site . 2>/dev/null || true
rm -rf /tmp/ixpage_bak

git add -A
git diff-index --quiet HEAD || git commit -m "sync members at $DATE"
git push -f git@github.com:PoemaIX/KSKB-IX.git HEAD:main
