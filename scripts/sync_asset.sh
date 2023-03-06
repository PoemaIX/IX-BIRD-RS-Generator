#!/bin/bash
cd /root/arouteserver/cache
# export RIPE_PASSWD="XXXXXXXXXXXXXXXXXXXXXXX"
/root/arouteserver/scripts/gen_ixpf.py | sed "s/fe80::/2404:f4c0:f70e:1980::/g" > /root/gitrs/KSKB-IX/static/files/ix-f.json
/root/arouteserver/scripts/gen_asset.py 1
/root/arouteserver/scripts/gen_asset.py 2

export AS_SET="AS-KSKB-IX"
export ARS_CLIENTS_PATH="/root/arouteserver/clients_all.yml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX.py

export AS_SET="AS-KSKB-IX-RS1"
export CLIENTS_ASSET_PATH="/root/gitrs/KSKB-IX/static/files/kskbix-rs1-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py

export AS_SET="AS-KSKB-IX-RS2"
export CLIENTS_ASSET_PATH="/root/gitrs/KSKB-IX/static/files/kskbix-rs2-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py --flat
