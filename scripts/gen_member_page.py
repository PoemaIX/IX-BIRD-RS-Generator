#!/usr/bin/python3
import requests
import json
import yaml
import ipaddress
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from ripe_asset_sync import parse_bird_protocols as get_bird_session, session_to_dict


#RS1_birdc = requests.get("http://[2404:f4c0:f70e:1980::1:1]:3234/bird?q=show+protocols+all").text
#RS1_info = session_to_dict(get_bird_session(birdc_output=RS1_birdc))
#RS1_baseurl = "https://ixlg.kskb.eu.org/__act__/2404:f4c0:f70e:1980::1:1/"

#RS2_birdc = requests.get("http://[2404:f4c0:f70e:1980::2:1]:3234/bird?q=show+protocols+all").text
#RS2_info = session_to_dict(get_bird_session(birdc_output=RS2_birdc))
#RS2_baseurl = "https://ixlg.kskb.eu.org/__act__/2404:f4c0:f70e:1980::2:1/"

#RS3_birdc = requests.get("http://[2404:f4c0:f70e:1980::3:1]:3234/bird?q=show+protocols+all").text
#RS3_info = session_to_dict(get_bird_session(birdc_output=RS3_birdc))
#RS3_baseurl = "https://ixlg.kskb.eu.org/__act__/2404:f4c0:f70e:1980::3:1/"

all_conf = yaml.safe_load( open("/root/arouteserver/clients_all.yml").read())

status = []
as_num = {}
def get_dict(default,d,klist):
    for k in klist:
        if k in d:
            d = d[k]
        else:
            return default
    return d
def add_dict(d,k,v):
    if k in d:
        d[k] += [v]
    else:
        d[k] = [v]

def get_route_md(num,action,base_url,name):
    if num == 0 or num == None:
        return f'[{ 0 }]({base_url.replace("__act__","detail") + name})'
    return f'[{ num }]({base_url.replace("__act__",action) + name})'

def get_member_route_md(base_url,info):
    name = info["name"]
    if info["state"] == "Established":
        return get_route_md(info["route"]["ipv6"]["imported"],"route_from_protocol_all",base_url,name) + "," + \
               get_route_md(info["route"]["ipv6"]["filtered"],"route_filtered_from_protocol_all",base_url,name)
    else:
        return f'[-]({base_url.replace("__act__","detail") + name })'

format_ip = lambda x:str(ipaddress.ip_address(x))

for i in range(len(all_conf["clients"])):
    item = {}
    conf = all_conf["clients"][i]
    asn = conf["asn"]
    index = len(get_dict([],as_num,[asn]))
    add_dict(as_num,asn,i)
    ips = [s["ip"] for s in conf["sessions"]]
    item["ASN"] = conf["asn"]
    item["Name"] = f'[{ conf["name"] }](https://bgp.tools/as/{asn})'
    item["AS-SET"] = ", ".join(conf["cfg"]["filtering"]["irrdb"]["as_sets"])
    item["RS R1"]  = "<br>".join(['<span neigh_ip="' + format_ip(ip) + '" rs="RSR1">-</span>' for ip in ips])
    item["RS T"]   = "<br>".join(['<span neigh_ip="' + format_ip(ip) + '" rs="RST">-</span>' for ip in ips])
    status += [item]

def tomark(listOfDicts):
    """Loop through a list of dicts and return a markdown table as a multi-line string.
    listOfDicts -- A list of dictionaries, each dict is a row
    """
    markdowntable = ""
    # Make a string of all the keys in the first dict with pipes before after and between each key
    markdownheader = '| ' + ' | '.join(map(str, listOfDicts[0].keys())) + ' |'
    # Make a header separator line with dashes instead of key names
    markdownheaderseparator = '|-----' * len(listOfDicts[0].keys()) + '|'
    # Add the header row and separator to the table
    markdowntable += markdownheader + '\n'
    markdowntable += markdownheaderseparator + '\n'
    # Loop through the list of dictionaries outputting the rows
    for row in listOfDicts:
        markdownrow = ""
        for key, col in row.items():
            markdownrow += '| ' + str(col) + ' '
        markdowntable += markdownrow + '|' + '\n'
    return markdowntable
    
md_output = """# Members

## AS-SET
* All members: [AS-KSKB-IX](https://apps.db.ripe.net/db-web-ui/lookup?source=RIPE&type=as-set&key=AS-KSKB-IX)
* RS Regular 1 connected members: [AS-KSKB-IX-RS1](https://apps.db.ripe.net/db-web-ui/lookup?source=RIPE&type=as-set&key=AS-KSKB-IX-RS1)
* RS Transitable connected members: [AS-KSKB-IX-RS2](https://apps.db.ripe.net/db-web-ui/lookup?source=RIPE&type=as-set&key=AS-KSKB-IX-RS2)

## Connection status

For real time data, check out our [Looking Glass](https://ixlg.kskb.eu.org/)

"""

md_output += tomark(status)

md_output += """
<script>
let rs_list = ["RSR1:2404:f4c0:f70e:1980::1:1","RST:2404:f4c0:f70e:1980::2:1"];
let lg_baseurl = "https://ixlg.kskb.eu.org/";
let lg_json_api = "https://ixlgjson.poema.net.eu.org/bird?RS=";

function get_state_url(num,name,type,proxy_url,baseurl){
    if (num === 0){
        type = "detail";
    }
    return `${baseurl}/${type}/${proxy_url}/${name}`;
}
async function render_mamber_list(rs_info){
    let rs_parts = rs_info.split(':');
    let [rs_name, proxy_url] = [rs_parts[0], rs_parts.slice(1).join(':')];
    let ixlg_api_resilt = await fetch(lg_json_api + rs_name);
    let clients = await ixlg_api_resilt.json();
    for (client of clients){
        let table_block = document.querySelectorAll(`[rs="${rs_name}"][neigh_ip="${client.addr.remote}"]` )[0]
        if ( table_block === undefined){ 
            console.log(`[rs="${rs_name}"][neigh_ip="${client.addr.remote}"]`);
            continue;
        };
        if ( client.state !== "Established" ){
            table_block.innerHTML = "-".link(get_state_url(0,client.name,"detail",proxy_url,lg_baseurl))
            continue;
        };
        let num_i = client.route.ipv6.imported;
        let num_f = client.route.ipv6.filtered;
        table_block.innerHTML = num_i.toString().link(get_state_url(num_i,client.name,"route_from_protocol_all",proxy_url,lg_baseurl)) + "," + 
        num_f.toString().link(get_state_url(num_f,client.name,"route_filtered_from_protocol_all",proxy_url,lg_baseurl));
    };
};
for( rs_info of rs_list){
    render_mamber_list(rs_info);
}
window.setInterval(function(){
    for( rs_info of rs_list){
        render_mamber_list(rs_info);
    }
}, 5000);
</script>
"""

open("/root/gitrs/KSKB-IX/docs/members.md","w").write(md_output)
