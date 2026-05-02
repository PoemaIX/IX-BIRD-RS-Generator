#!/bin/bash
set -eo pipefail
export PYTHONPATH="/root/gitrs/RIPE-AS-SET-SYNC:$PYTHONPATH"
cd /root/arouteserver/cache

/root/arouteserver/scripts/gen_ixpf.py | sed "s/fe80::/2404:f4c0:f70e:1980::/g" > /root/gitrs/KSKB-IX/static/files/ix-f.json
/root/arouteserver/scripts/gen_estab.py

export AS_SET="AS-KSKB-IX"
export ARS_CLIENTS_PATH="/root/arouteserver/clients_all.yml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/sync_from_config.py || echo "::warning::Failed to sync AS-KSKB-IX to RIPE"

export AS_SET="AS-KSKB-IX-RS1"
export CLIENTS_ASSET_PATH="/root/gitrs/KSKB-IX/static/files/kskbix-rs1-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/sync_from_estab.py || echo "::warning::Failed to sync AS-KSKB-IX-RS1 to RIPE"

export AS_SET="AS-KSKB-IX-RS2"
python3 /root/gitrs/RIPE-AS-SET-SYNC/sync_from_routes.py || echo "::warning::Failed to sync AS-KSKB-IX-RS2 to RIPE"
