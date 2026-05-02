# IX-BIRD-RS-Generator

Automated BIRD route server configuration generator for [Poema-IX](https://ix.poema.eu.org/) (Poema IX).  
Runs daily via GitHub Actions to regenerate BGP configurations, sync AS-SET data to the RIPE database, and update the IXP member page.

## Overview

Poema-IX operates two route servers (RS Peering and RS Transitable) running on a [custom fork of BIRD 2.18](https://github.com/KusakabeShi/bird/tree/release-v2.18-add-ll) on AS199594. This project uses the custom fork of [ARouteServer](https://github.com/PoemaIX/arouteserver) as the templating engine to produce BIRD configurations from a declarative client list, then synchronizes the membership state to RIPE and publishes a live status page.

**RS Peering** — standard route server, rejects routes containing Tier-1 ASNs in the path.  
**RS Transitable** — transitable route server, applies stricter prefix filtering (AS-SETs with >100 prefixes or containing T1 ASNs).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Actions  (regen-all.yml — daily 00:00 UTC)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Setup (SSH keys, OpenVPN to IX fabric)                      │
│                                                                 │
│  2. gen_rs.sh                                                   │
│     ├─ gen_rs.py 2 → clients_rs2.yml                            │
│     ├─ arouteserver bird → bird_rs2.conf                        │
│     ├─ gen_rs.py 1 → clients_rs1.yml                            │
│     └─ arouteserver bird → bird_rs1.conf                        │
│                                                                 │
│  3. sync_asset.sh                                               │
│     ├─ gen_ixpf.py        → IX-F member export JSON             │
│     ├─ gen_estab.py       → per-RS establishment YAML           │
│     └─ RIPE-AS-SET-SYNC   → sync AS-SETs to RIPE DB             │
│        ├─ sync_from_config.py  (AS-KSKB-IX — all members)       │
│        ├─ sync_from_estab.py   (AS-KSKB-IX-RS1 — established)   │
│        └─ sync_from_routes.py  (AS-KSKB-IX-RS2 — active routes) │
│                                                                 │
│  4. sync_ixpage.sh                                              │
│     ├─ gen_member_page.py → members.md                          │
│     ├─ mkdocs build       → static site                         │
│     └─ git push           → KSKB-IX website repo                │
│                                                                 │
│  5. git filter-repo (strip large .conf from history) & push     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Workflows

### `regen-all.yml` (Primary)

Full pipeline: generate BIRD configs, sync RIPE AS-SETs, rebuild IX website.

| Trigger | Schedule |
|---------|----------|
| Cron | Daily at 00:00 UTC |
| Manual | `workflow_dispatch` with optional log level |

Requires VPN connectivity to the IX fabric to query live BIRD daemons for session state.

### `sync-asset.yml` (Lightweight)

Runs only the asset sync and IXPage steps — skips BIRD config generation. Useful for refreshing member status without a full rebuild.

| Trigger | Schedule |
|---------|----------|
| Manual | `workflow_dispatch` only |

## Key Files

| Path | Purpose |
|------|---------|
| `clients_all.yml` | Master list of all IX members (ASN, sessions, AS-SETs) |
| `general.yml` | Route server policy (filtering, communities, RPKI) |
| `arouteserver.yml` | ARouteServer engine configuration |
| `templates/bird/` | Jinja2 templates for BIRD config generation |
| `scripts/gen_rs.py` | Splits `clients_all.yml` into per-RS client files with policy |
| `scripts/gen_ixpf.py` | Generates IX-F member export JSON from live BIRD state |
| `scripts/gen_estab.py` | Generates establishment status YAML per route server |
| `scripts/gen_member_page.py` | Produces the live member status page (Markdown + JS) |
| `bird_rs1.conf` / `bird_rs2.conf` | Generated BIRD configs (excluded from git history) |

## RIPE-AS-SET-SYNC

A companion Python library ([PoemaIX/RIPE-AS-SET-SYNC](https://github.com/PoemaIX/RIPE-AS-SET-SYNC)) that synchronizes IX membership to RIPE database AS-SET objects using X.509 certificate authentication.

Three sync strategies are used:

| Script | Target AS-SET | Data Source |
|--------|---------------|-------------|
| `sync_from_config.py` | AS-KSKB-IX | All configured members in `clients_all.yml` |
| `sync_from_estab.py` | AS-KSKB-IX-RS1 | Members with established BGP sessions on RS1 |
| `sync_from_routes.py` | AS-KSKB-IX-RS2 | Origin ASNs from active routes on RS2 (excluding STUIX transit) |

## Dependencies

- **Python**: ARouteServer, requests, pyyaml, jieba, mkdocs
- **System**: `bgpq4` (IRR queries), `openvpn` (IX fabric access), `git-filter-repo`
- **External Repos**: [PoemaIX/arouteserver](https://github.com/PoemaIX/arouteserver), [PoemaIX/KSKB-IX](https://github.com/PoemaIX/KSKB-IX), [PoemaIX/RIPE-AS-SET-SYNC](https://github.com/PoemaIX/RIPE-AS-SET-SYNC)

## Network Details

- **IX AS**: 199594
- **Peering LAN**: `2404:f4c0:f70e:1980::/64` (IPv6), link-local sessions supported
- **BIRD API**: RS1 at `[2404:f4c0:f70e:1980::1:1]:3234`, RS2 at `[2404:f4c0:f70e:1980::2:1]:3234`
- **IXF ID**: 1061

## License

MIT
