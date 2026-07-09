# Preflight log

## Local worktree

Command: `git status --short`

Output was empty before evidence files were created, confirming a clean local worktree

## Fedora stack path

- SSH host: `fedora`
- Stack path: `/home/staticduo/docker/litellm`
- Stack path exists and is a directory
- Compose file: `/home/staticduo/docker/litellm/docker-compose.yaml`

## Compose image settings before deploy

```text
compose_image_settings:
file=/home/staticduo/docker/litellm/docker-compose.yaml
  line=3 service=litellm image: ${LITELLM_IMAGE:-docker.staticduo.com/litellm:latest}
  line=68 service=redis image: redis:7.4-alpine

.env image setting:
line=17 LITELLM_IMAGE=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707
```

## Container status before deploy

```text
name=/litellm id=eb6889ed1d1b7048065969829cb2cdf32d057d6a4a045f36a1c4cbc7ee6bc637 image=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707 image_id=sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86 status=running health=healthy
name=/litellm-admin-mcp id=79bd26a5dfbd2d3a731250a042c02d50136e7068f5a23cf7c473d41de0f1f36b image=litellm-litellm-admin-mcp image_id=sha256:20e833e38f331212ab950c0f58b5dcd3ecc8e8a9fc5f6e9e39762a16d2ec163b status=running health=healthy
name=/litellm-admin-mcp-compat id=a8be5956ef9bab786aee750149546087dbc4ade883e9c774c12f2cbbc05fc1a6 image=litellm-litellm-admin-mcp-compat image_id=sha256:20dfbfd69744af437002a0a30c7e63dc7698e1549d21c0e8329bc0d956fa12fa status=running health=healthy
name=/litellm-redis id=83e769a0bed4d1781977ef601b5ba741e7fba6b256b5d9a760751a70de938fd5 image=redis:7.4-alpine image_id=sha256:6ab0b6e7381779332f97b8ca76193e45b0756f38d4c0dcda72dbb3c32061ab99 status=running health=healthy
```

## Image digest references before deploy

```text
image=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707 id=sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86 repo_digests=docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86
```

## Rollback reference

Previous image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`

Rollback command convention from `/home/staticduo/docker/litellm`: set `.env` `LITELLM_IMAGE` back to the previous image, then run `docker compose pull litellm && docker compose up -d --no-deps litellm`
