#!/bin/bash
cd /root/arouteserver
export AS_SET="AS-KSKB-IX"
# export RIPE_PASSWD="XXXXXXXXXXXXXXXXXXXXXXX"
export ARS_CLIENTS_PATH="/root/arouteserver/clients_all.yml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX.py

export AS_SET="AS-KSKB-IX-RS1"
export CLIENTS_ASSET_PATH="/root/gitrs/KSKB-IX/static/files/kskbix-rs1-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py

export AS_SET="AS-KSKB-IX-RS2"
export CLIENTS_ASSET_PATH="/root/gitrs/KSKB-IX/static/files/kskbix-rs2-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py --flat
