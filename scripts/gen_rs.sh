#!/bin/bash
export PYTHONPATH=/root/gitrs/ars
set -x
set -e

cp /root/arouteserver/scripts/__pycache__/.gitignore /root/arouteserver/cache/.gitignore

cd /root/gitrs/ars
/root/arouteserver/scripts/gen_rs.py 2
cp /root/arouteserver/clients_rs2.yml /root/arouteserver/clients.yml
scripts/arouteserver bird -o /root/arouteserver/bird_rs2.conf.out --target-version 2.0.8
mv /root/arouteserver/bird_rs2.conf.out /root/arouteserver/bird_rs2.conf
cd /root/arouteserver/
md5sum bird_rs2.conf > /root/arouteserver/bird_rs2.conf.md5

cd /root/gitrs/ars
/root/arouteserver/scripts/gen_rs.py 1
cp /root/arouteserver/clients_rs1.yml /root/arouteserver/clients.yml
scripts/arouteserver bird -o /root/arouteserver/bird_rs1.conf.out --target-version 2.0.8
mv /root/arouteserver/bird_rs1.conf.out /root/arouteserver/bird_rs1.conf
cd /root/arouteserver/
md5sum bird_rs1.conf > /root/arouteserver/bird_rs1.conf.md5

cd /root/gitrs/ars
# scripts/arouteserver ixf-member-export --clients /root/arouteserver/clients_rs1.yml "KSKB-IX" 1 | sed "s/fe80::/2404:f4c0:f70e:1980::/g" > /root/gitrs/KSKB-IX/static/files/ix-f.json



