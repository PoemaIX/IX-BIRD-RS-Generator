#!/usr/bin/python3
import requests
import yaml
import sys
import subprocess
import os
import json
import time
from bird_parser import get_bird_session
client = yaml.safe_load( open("/root/arouteserver/clients_all.yml").read())
yaml.SafeDumper.ignore_aliases = lambda self, data: True

# get all as-set
client_list = client["clients"]
client_as_set = [(c["asn"],c["cfg"]["filtering"]["irrdb"]["as_sets"]) for c in client_list]
client_as_set = {c[0]:c[1] if c[1] != [] else ["AS" + str(c[0])] for c in client_as_set}
open("/root/gitrs/KSKB-IX/static/files/kskbix-all.yaml","w").write(yaml.safe_dump(client_as_set))

RS1_birdc = requests.get("http://[2404:f4c0:f70e:1980::1:1]:3234/bird?q=show+protocols+all").text
RS1_info  = get_bird_session(birdc_output=RS1_birdc)
RS1_estab = set(map(lambda x:x["as"]["remote"],filter(lambda x:x["state"] == "Established" and x["route"]["ipv6"]["imported"] > 0 ,RS1_info)))

RS2_birdc = requests.get("http://[2404:f4c0:f70e:1980::2:1]:3234/bird?q=show+protocols+all").text
RS2_info  = get_bird_session(birdc_output=RS2_birdc)
RS2_estab = set(map(lambda x:x["as"]["remote"],filter(lambda x:x["state"] == "Established" and x["route"]["ipv6"]["imported"] > 0 ,RS2_info)))

expire = 86400

irr_cache = {}
irr_cache_path = "/root/arouteserver/scripts/irr_cache.json"
if os.path.isfile(irr_cache_path):
    try:
        irr_cache = json.loads(open(irr_cache_path).read())
    except:
        irr_cache = {}
def getlen(as_set_all,af):
    if as_set_all in irr_cache and ( irr_cache[as_set_all]["time"] + expire ) > time.time():
        #print(as_set_all,irr_cache[as_set_all]["result"])
        return irr_cache[as_set_all]["result"]
    # irrdb = "RIPE,APNIC,AFRINIC,ARIN,LACNIC" # "RIPE,APNIC,AFRINIC,ARIN,NTTCOM,ALTDB,BBOI,BELL,JPIRR,LEVEL3,RADB,TC" 
    irrdb = "RIPE,APNIC,AFRINIC,ARIN,NTTCOM,ALTDB,BBOI,BELL,JPIRR,LEVEL3,RADB,TC" 
    as_set = as_set_all
    if "::" in as_set_all:
        irrdb,as_set = as_set.split("::")
    #print(" ".join(["bgpq4", "-" + str(af), "-b", "-R", "48","-S",irrdb, "-m", "48" , as_set]))
    bgpq4_out = subprocess.run(["bgpq4", "-" + str(af), "-b", "-R", "48","-S",irrdb, "-m", "48" , as_set], stdout=subprocess.PIPE)
    bgpq4_asns = subprocess.run(["bgpq4", "-" + str(af), "-tj", "-S",irrdb , as_set], stdout=subprocess.PIPE).stdout.decode()
    asset_asns = json.loads(bgpq4_asns)["NN"]
    irr_cache[as_set_all] = {}
    irr_cache[as_set_all]["ASNs"] = asset_asns
    irr_cache[as_set_all]["result"] = max(0,len(bgpq4_out.stdout.decode().split("\n"))-2)
    irr_cache[as_set_all]["time"] = time.time()
    #print(as_set_all,irr_cache[as_set_all]["result"])
    return irr_cache[as_set_all]["result"]

as_sets_all = {}
as_sets_estab = {}
as_sets_all_all = []
as_sets_estab_all = []

def merge_dict_list(dl):
    dr = {}
    dl = list(dl)
    for d in dl:
        for k,v in d.items():
            if k not in dr:
                if type(v) == list:
                    dr[k] = v.copy()
                else:
                    dr[k] = [v]
            else:
                if type(v) == list:
                    dr[k] += v
                else:
                    dr[k] += [v]
    for k,v in dr.items():
        dr[k] = list(dict.fromkeys(v).keys())
    return dr

if sys.argv[1] == "2":
    for ci in range(len(client["clients"])):
        the_asn = client["clients"][ci]["asn"]
        as_sets_new = []
        for as_set in client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]:
            if getlen(as_set,6) <= 100:
                as_sets_new += [as_set]
        asset_info = {"asn": the_asn}
        asset_info["as-set"] = as_sets_new if len(as_sets_new) > 0 else ["AS" + str(the_asn)]
        asset_info["as-set-flat"] = []
        for asset in asset_info["as-set"]:
            asset_info["as-set-flat"] += irr_cache[asset]["ASNs"] if asset in irr_cache else [the_asn]
        as_sets_all[ci] = asset_info
        if the_asn in RS2_estab:
            as_sets_estab[ci] = asset_info
    as_sets_all_all = merge_dict_list(as_sets_all.values())
    as_sets_estab_all = merge_dict_list(as_sets_estab.values())
    as_sets_all["all"] = as_sets_all_all
    as_sets_estab["all"] = as_sets_estab_all
    open("/root/gitrs/KSKB-IX/static/files/kskbix-rs2.yaml","w").write(yaml.safe_dump(as_sets_all))
    open("/root/gitrs/KSKB-IX/static/files/kskbix-rs2-estab.yaml","w").write(yaml.safe_dump(as_sets_estab))
if sys.argv[1] == "1":
    for ci in range(len(client["clients"])):
        the_asn = client["clients"][ci]["asn"]
        my_as_sets = client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]
        asset_info = {"asn": the_asn}
        asset_info["as-set"] = my_as_sets if len(my_as_sets) > 0 else ["AS" + str(the_asn)]
        asset_info["as-set-flat"] = []
        for asset in asset_info["as-set"]:
            asset_info["as-set-flat"] += irr_cache[asset]["ASNs"] if asset in irr_cache else [the_asn]
        as_sets_all[ci] = asset_info
        if the_asn in RS1_estab:
            as_sets_estab[ci] = asset_info
    as_sets_all_all = merge_dict_list(as_sets_all.values())
    as_sets_estab_all = merge_dict_list(as_sets_estab.values())
    as_sets_all["all"] = as_sets_all_all
    as_sets_estab["all"] = as_sets_estab_all
    open("/root/gitrs/KSKB-IX/static/files/kskbix-rs1.yaml","w").write(yaml.safe_dump(as_sets_all))
    open("/root/gitrs/KSKB-IX/static/files/kskbix-rs1-estab.yaml","w").write(yaml.safe_dump(as_sets_estab))
open(irr_cache_path,"w").write(json.dumps(irr_cache,indent=4))
