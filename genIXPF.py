#!/bin/python3
import datetime
import json
import requests
import yaml
from bird_parser import get_bird_session
client = yaml.safe_load( open("/root/arouteserver/clients_all.yml").read())
yaml.SafeDumper.ignore_aliases = lambda self, data: True

RS1_birdc = requests.get("http://[2404:f4c0:f70e:1980::1:1]:3234/bird?q=show+protocols+all").text
RS1_info  = get_bird_session(birdc_output=RS1_birdc)
RS1_estab = set(map(lambda x:x["as"]["remote"],filter(lambda x:x["state"] == "Established" and x["route"]["ipv6"]["imported"] > 0 ,RS1_info)))

# prepare ixp_list data
ixp_list = [{
    "ixp_id": 0,
    "ixf_id": 1061,
    "shortname": "KSKB-IX",
    "vlan": [
        {"id": 0}
    ],
    "switch": [
        {
            "id": 1,
            "name": "main switch",
            "colo": "KSKB Home",
            "city": "Taiwan",
            "country": "TW",
            "manufacturer": "unknown",
            "model": "unknown"
        }
    ]
}]

# prepare member_list data
member_list = [
  {
    "asnum": 199594,
    "connection_list": [
      {
        "ixp_id": 0,
        "state": "active",
        "if_list": [
          {
            "if_speed": 250,
            "switch_id": 1
          }
        ],
        "vlan_list": [
          {
            "vlan_id": 0,
            "ipv6": {
              "address": "2404:f4c0:f70e:1980::1:1",
              "as_macro": "AS-KSKB-IX-RS1",
              "routeserver": True
            }
          },
          {
            "vlan_id": 0,
            "ipv6": {
              "address": "2404:f4c0:f70e:1980::2:1",
              "as_macro": "AS-KSKB-IX-RS2",
              "routeserver": True
            }
          }
        ]
      }
    ]
  }
]
for ci in range(len(client["clients"])):
    asnum = client["clients"][ci]["asn"]
    as_macros = client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]
    as_macro = as_macros[0] if len(as_macros) > 0 else ""
    routeserver = asnum in RS1_estab
    state = "active" if routeserver else "inactive"
    connection_item = {
        "ixp_id": 0,
        "state": state,
        "if_list": [
            {
                "if_speed": 250,
                "switch_id": 1
            }
        ],
        "vlan_list": [
            {
                "vlan_id": 0,
                "ipv6": {
                    "address": client["clients"][ci]["ip"],
                    "as_macro": as_macro,
                    "routeserver": routeserver
                }
            }
        ]
    }
    member_item = {
        "asnum": asnum,
        "connection_list": [connection_item]
    }
    member_list.append(member_item)

# prepare the JSON structure
data_dict = {
    "version": "1.0",
#    "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
    "ixp_list": ixp_list,
    "member_list": member_list,
}

# convert to JSON
json_data = json.dumps(data_dict, indent=2)
print(json_data)
