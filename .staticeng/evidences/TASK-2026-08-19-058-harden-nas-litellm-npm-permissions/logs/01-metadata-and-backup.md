# Metadata And Protected Backup

## Pre-change metadata

| Path | Owner | Mode | Size | Inode | Symlink |
|---|---:|---:|---:|---:|---|
| `/volume2/docker` | `0:0` | `0777` | 4096 | 102039553 | no |
| `/volume2/docker/litellm` | `1000:10` | `0777` | 4096 | 113386177 | no |
| `/volume2/docker/litellm/.env` | `0:0` | `0777` | 1217 | 113397217 | no |
| `/volume2/docker/litellm-staging` | `1000:10` | `0700` | 4096 | 114952492 | no |
| `/volume2/docker/litellm-staging/.env` | `1000:10` | `0777` | 1174 | 114959486 | no |
| `/volume2/docker/npm` | `0:0` | `0777` | 4096 | 102039850 | no |
| `/volume2/docker/npm/data` | `0:0` | `0777` | 4096 | 102107529 | no |
| `/volume2/docker/npm/data/nginx` | `0:0` | `0777` | 4096 | 102107538 | no |
| `/volume2/docker/npm/data/nginx/proxy_host` | `0:0` | `0777` | 4096 | 102107721 | no |
| `/volume2/docker/npm/data/nginx/proxy_host/62.conf` | `0:0` | `0777` | 2171 | 102105352 | no |

ACL metadata showed world-write through effective `other::rwx` entries. No target was a symlink

## Protected rollback

Rollback root: `/volume2/docker/litellm/releases/20260819T160419Z-TASK-2026-08-19-058-harden-nas-litellm-npm-permissions`

| Artifact | Owner | Mode | Size |
|---|---:|---:|---:|
| Rollback directory | `0:0` | `0700` | 4096 |
| `prod-env.rollback` | `0:0` | `0600` | 1217 |
| `staging-env.rollback` | `0:0` | `0600` | 1174 |
| `npm-host-62.rollback` | `0:0` | `0600` | 2171 |
| `prechange-metadata.txt` | `0:0` | `0600` | 1247 |

Byte comparison confirmed each protected `.env` rollback matched its live source. No secret content or content hash was read into evidence
