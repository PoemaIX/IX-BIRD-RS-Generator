#!/usr/bin/python3
import requests
import yaml
import sys
import os
import json
import traceback
import copy
from ripe_asset_sync import IrrCache, load_clients, extract_client_as_sets

client = yaml.safe_load( open("/root/arouteserver/clients_all.yml").read())
yaml.SafeDumper.ignore_aliases = lambda self, data: True

try:
    x = requests.get('https://ixpm.stuix.io/api/v4/member-export/ixf/1.0')
    x.raise_for_status()
    stuix_members = [m["asnum"] for m in json.loads(x.text)["member_list"]]
    open("stuix_members.json","w").write(json.dumps(stuix_members))
except Exception as e:
    print(traceback.format_exc())
    stuix_members = json.loads(open("stuix_members.json","r").read())

# get all as-set
clients_list = load_clients("/root/arouteserver/clients_all.yml")
client_as_set = extract_client_as_sets(clients_list)
open("/root/gitrs/KSKB-IX/static/files/kskbix-all.yaml","w").write(yaml.safe_dump(client_as_set))

expanded_clients = []
for c in client["clients"]:
    for sess in c["sessions"]:
        entry = copy.deepcopy(c)
        entry["ip"] = sess["ip"]
        del entry["sessions"]
        expanded_clients.append(entry)
client["clients"] = expanded_clients

irr = IrrCache("/root/arouteserver/cache/irr_cache.json")


if sys.argv[1] == "2":
    for ci in range(len(client["clients"])):
        the_asn = client["clients"][ci]["asn"]
        del  client["clients"][ci]["name"]
        as_sets_new = []
        for as_set in client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]:
            as_set_info = irr.query(as_set,6)
            if int(the_asn) in stuix_members:
                if "attach_custom_communities" not in client["clients"][ci]["cfg"]:
                    client["clients"][ci]["cfg"]["attach_custom_communities"] = ["as_path_from_stuix"]
                else:
                    client["clients"][ci]["cfg"]["attach_custom_communities"] +=  ["as_path_from_stuix"]
            elif "enforce_origin_in_as_set" in client["clients"][ci]["cfg"]["filtering"]["irrdb"]:
                if "attach_custom_communities" not in client["clients"][ci]["cfg"]:
                    client["clients"][ci]["cfg"]["attach_custom_communities"] = ["as_path_from_stuix"]
                else:
                    client["clients"][ci]["cfg"]["attach_custom_communities"] +=  ["as_path_from_stuix"]
            elif as_set_info["prefix_num"] <= 100 and as_set_info["t1_asns"] == []:
                as_sets_new += [as_set]
            else:
                if as_set_info["t1_asns"] != []:
                    print("Warning:",as_set ,"contains t1_asns:",as_set_info["t1_asns"])
        client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"] = as_sets_new
    client_rs2_txt = yaml.safe_dump(client, sort_keys=False)
    open("/root/arouteserver/clients_rs2.yml","w").write(client_rs2_txt)
if sys.argv[1] == "1":
    for ci in range(len(client["clients"])):
        the_asn = client["clients"][ci]["asn"]
        del  client["clients"][ci]["name"]
        as_sets_new = []
        for as_set in client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]:
            as_set_info = irr.query(as_set,6)
            if as_set_info["t1_asns"] == []:
                as_sets_new += [as_set]
            else:
                if as_set_info["t1_asns"] != []:
                    print("Warning:",as_set ,"contains t1_asns:",as_set_info["t1_asns"])
        client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"] = as_sets_new
        client["clients"][ci]["cfg"]["filtering"]["irrdb"].pop("enforce_origin_in_as_set",None)
        client["clients"][ci]["cfg"]["filtering"]["irrdb"].pop("enforce_prefix_in_as_set",None)
        client["clients"][ci]["cfg"]["filtering"].pop("transit_free",None)
        client["clients"][ci]["cfg"]["filtering"].pop("max_prefix",None)
        my_as_sets = client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]
    client_rs1_txt = yaml.safe_dump(client, sort_keys=False)
    open("/root/arouteserver/clients_rs1.yml","w").write(client_rs1_txt)
irr.save()
