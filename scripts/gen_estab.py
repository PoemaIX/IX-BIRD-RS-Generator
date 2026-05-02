#!/usr/bin/python3
import requests
import yaml
from ripe_asset_sync import parse_bird_protocols, filter_established_sessions, load_clients, extract_client_as_sets, IrrCache

client_path = "/root/arouteserver/clients_all.yml"
clients = load_clients(client_path)
client_as_set = extract_client_as_sets(clients)
yaml.SafeDumper.ignore_aliases = lambda self, data: True
open("/root/gitrs/KSKB-IX/static/files/kskbix-all.yaml", "w").write(yaml.safe_dump(client_as_set))

RS1_birdc = requests.get("http://[2404:f4c0:f70e:1980::1:1]:3234/bird?q=show+protocols+all").text
RS1_estab = filter_established_sessions(parse_bird_protocols(birdc_output=RS1_birdc))

RS2_birdc = requests.get("http://[2404:f4c0:f70e:1980::2:1]:3234/bird?q=show+protocols+all").text
RS2_estab = filter_established_sessions(parse_bird_protocols(birdc_output=RS2_birdc))

irr = IrrCache("/root/arouteserver/cache/irr_cache.json")


def merge_dict_list(dl):
    dr = {}
    dl = list(dl)
    for d in dl:
        for k, v in d.items():
            if k not in dr:
                dr[k] = v.copy() if type(v) == list else [v]
            else:
                dr[k] += v if type(v) == list else [v]
    for k, v in dr.items():
        dr[k] = list(dict.fromkeys(v).keys())
    return dr


def gen_estab(rs_name, estab_set, filter_prefix=False):
    as_sets_all = {}
    as_sets_estab = {}

    for ci in range(len(clients)):
        the_asn = clients[ci]["asn"]
        as_sets_new = []
        for as_set in clients[ci]["cfg"]["filtering"]["irrdb"]["as_sets"]:
            info = irr.query(as_set, 6)
            if filter_prefix:
                if info["prefix_num"] <= 100 and info["t1_asns"] == []:
                    as_sets_new.append(as_set)
                elif info["t1_asns"] != []:
                    print("Warning:", as_set, "contains t1_asns:", info["t1_asns"])
            else:
                if info["t1_asns"] == []:
                    as_sets_new.append(as_set)
                elif info["t1_asns"] != []:
                    print("Warning:", as_set, "contains t1_asns:", info["t1_asns"])

        asset_info = {"asn": the_asn}
        asset_info["as-set"] = as_sets_new if as_sets_new else ["AS" + str(the_asn)]
        asset_info["as-set-flat"] = []
        for asset in asset_info["as-set"]:
            cached = irr.get(asset)
            asset_info["as-set-flat"] += cached["ASNs"] if cached else [the_asn]
        as_sets_all[ci] = asset_info
        if the_asn in estab_set:
            as_sets_estab[ci] = asset_info

    as_sets_all["all"] = merge_dict_list(as_sets_all.values())
    as_sets_estab["all"] = merge_dict_list(as_sets_estab.values())

    open(f"/root/gitrs/KSKB-IX/static/files/kskbix-{rs_name}.yaml", "w").write(yaml.safe_dump(as_sets_all))
    open(f"/root/gitrs/KSKB-IX/static/files/kskbix-{rs_name}-estab.yaml", "w").write(yaml.safe_dump(as_sets_estab))


gen_estab("rs1", RS1_estab, filter_prefix=False)
gen_estab("rs2", RS2_estab, filter_prefix=True)
irr.save()
