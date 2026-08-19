# Permissions And NPM Regeneration

## Final permissions

| Path | Owner | Mode |
|---|---:|---:|
| `/volume2/docker` | `0:0` | `0770` |
| `/volume2/docker/litellm` | `1000:10` | `0750` |
| `/volume2/docker/litellm/.env` | `1000:10` | `0600` |
| `/volume2/docker/litellm/docker-compose.yaml` | `1000:10` | `0600` |
| `/volume2/docker/litellm/start-litellm.sh` | `1000:10` | `0750` |
| `/volume2/docker/litellm/releases` | `1000:10` | `0750` |
| `/volume2/docker/litellm-staging` | `1000:10` | `0700` |
| `/volume2/docker/litellm-staging/.env` | `1000:10` | `0600` |
| `/volume2/docker/litellm-staging/docker-compose.yaml` | `1000:10` | `0600` |
| `/volume2/docker/litellm-staging/start-litellm.sh` | `1000:10` | `0750` |
| `/volume2/docker/npm` | `0:0` | `0755` |
| `/volume2/docker/npm/data` | `0:0` | `0755` |
| `/volume2/docker/npm/data/nginx` | `0:0` | `0755` |
| `/volume2/docker/npm/data/nginx/proxy_host` | `0:0` | `0755` |
| `/volume2/docker/npm/data/nginx/proxy_host/62.conf` | `0:0` | `0644` |

The deployment owner retained required access to both `.env` files and deployment paths. The complete target world-write gate passed

## Supported regeneration

- NPM runs as root with umask `0022`
- A supported host 62 API update preserved `http://litellm-production:4000`, TLS certificate 1, and SSL enablement
- Host 62 was regenerated at a new inode while retaining size 2171 and byte-identical content
- Regenerated host 62 mode was `0644` without post-generation repair
- NPM remained healthy and authenticated with admin access
- `nginx -t` passed after regeneration
- NPM resolved `litellm-production` to exactly `172.28.0.29`
- A root-in-container create/chmod/remove probe in `proxy_host` passed and produced mode `0644`
- A delayed permission check confirmed host 62 remained `0644` and all required parent modes remained `0755`
- Inventory found 112 generated proxy-host configs and zero world-writable configs; no unrelated host was changed by the targeted update
