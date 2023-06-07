#!/usr/bin/python3
import requests
import json
import yaml
import ipaddress
import sys
import os
import argparse
import copy
from subprocess import PIPE, Popen
from pathlib import Path

RS2_down_asns = {}
RS2_down_routes_txt = requests.get("http://[2404:f4c0:f70e:1980::2:1]:3234/bird?q=show%20route%20where%20%28199594%2C65530%2C7%29%21~bgp_large_community%26%26source%3DRTS_BGP%20all").text
for textline in RS2_down_routes_txt.split("\n"):
    if "as_path" in textline:
        bgp_last = textline.split(" ")[-1]
        if bgp_last.isnumeric():
            RS2_down_asns[int(bgp_last)] = 0

as_set = os.environ["AS_SET"]
password = os.environ["RIPE_PASSWD"]

url = f"https://rest.db.ripe.net/ripe/as-set/{as_set}?password={password}"

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

def extract_member(base_json):
    return list(map(lambda x:x["value"],filter(lambda x:x["name"] == "members", base_json["objects"]["object"][0]["attributes"]["attribute"])))
def index_of_first(lst, pred):
    for i, v in enumerate(lst):
        if pred(v):
            return i
    return 1
def pack_member(base_json,member_list):
    base_json = copy.deepcopy(base_json)
    old_list = base_json["objects"]["object"][0]["attributes"]["attribute"]
    first_member_idx = index_of_first(old_list,lambda x:x["name"] == "members")
    old_list = list(filter(lambda x:x["name"] != "members",old_list))
    new_list = old_list[0:first_member_idx] + [{"name": "members", "value": member, "referenced-type":"aut-num" if member[:2] == "AS" and member[2:].isdecimal() else "as-set" } for member in member_list] + old_list[first_member_idx:]
    for item in new_list:
        item.pop("comment", None)
    base_json["objects"]["object"][0]["attributes"]["attribute"] = new_list
    return base_json

base_json_save = Path(as_set + "_last.json")
if base_json_save.is_file():
    base_json_old = json.loads(open(base_json_save).read())
else:
    base_json_old = json.loads(requests.request("GET", url, headers=headers).text)
    
base_json_new = base_json_old
ixmember_old = extract_member(base_json_old)

ixmember_new = map(lambda x:"AS" + str(x),RS2_down_asns.keys())

if ixmember_old != ixmember_new:
    new_json = pack_member(base_json_old,ixmember_new)
    payload = json.dumps(new_json)
    response = requests.request("PUT", url, headers=headers, data=payload)
    response.raise_for_status()
    base_json_new = json.loads(response.text)
    print("updated:",as_set)
else:
    print("same, no update:",as_set)

open(base_json_save,"w").write(json.dumps(base_json_new))