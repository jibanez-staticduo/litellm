# LiteLLM 1.98.0 NAS and Fedora Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release fork commit `8e074a3c6ac3522a29aaffbc490aa44613c65af8` as LiteLLM `1.98.0` to Fedora first and NAS second, using one immutable image digest with independent verification and rollback for each host

**Architecture:** Build once from a detached worktree of the published fork `main`, push an immutable tag, resolve its registry digest, and deploy that exact digest to both amd64 hosts. Fedora is the canary and must pass functional checks plus a soak window before NAS is touched; the stable tag moves only after both hosts pass. Each host keeps its existing Compose/config differences and independent PostgreSQL data while only the LiteLLM application image changes

**Tech Stack:** Git worktrees, Docker BuildKit, private Docker registry, Docker Compose, LiteLLM Proxy `1.98.0`, PostgreSQL, Redis, Codex CLI, LazyMCP, Python HTTP probes

## Global Constraints

- Release source is fork `origin/main` at exact SHA `8e074a3c6ac3522a29aaffbc490aa44613c65af8`
- Release version is `1.98.0`
- Immutable image tag is `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817`
- Fedora is the canary; NAS is not changed until Fedora passes all checks and a 15-minute soak
- Build one image and deploy the same registry digest to both hosts
- Preserve each host's `.env`, `config.yaml`, startup wrapper, LazyMCP wrapper, data directory, Redis volume, PostgreSQL database, model inventory, routes, fallbacks, and host-specific configuration
- Never print `.env`, credentials, authorization headers, database URLs, token files, or container arguments containing secrets
- Do not use `/home/staticduo/git/release-litellm.sh` for this release: it expects a missing worktree and nonexistent `fork` remote, deploys NAS before Fedora, moves stable before validation, and only prepares NAS rollback
- Do not use a plain HTTP 200 as the acceptance gate; validate version, digest, health, models, Responses, LazyMCP, logs, Codex, restarts, and OOM state independently on each host
- A database restore is a destructive last resort because it discards writes made after the backup; application-image rollback is always attempted first

---

## Observed Baseline

| Item | NAS | Fedora |
|---|---|---|
| Compose file | `/volume2/docker/litellm/docker-compose.yaml` | `/home/staticduo/docker/litellm/docker-compose.yaml` |
| Current app image | `litellm:litellm-nas-stream-regression-002` | `local/litellm-codex-stream:002-9e7a49493b-20260805` |
| Current app image ID | `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa` | `sha256:dca542cdb661c3c38d029bb960541e10cabc2f33be6baf4259f46b489c32eac3` |
| Current LiteLLM version | `1.92.0` | `1.92.0` |
| Runtime state | healthy, 0 restarts, no OOM | healthy, 0 restarts, no OOM |
| Compose app image source | hard-coded local tag | hard-coded local tag |
| PostgreSQL | local `postgresql`, database `litellm`, address observed as `172.18.0.16` | local `postgresql`, database `litellm`, address observed as `172.21.0.22` |
| Free space | 3.5 TiB on `/volume2` | 1005 GiB on `/home` |

The two PostgreSQL services are independent local endpoints. Canary database migrations on Fedora therefore do not mutate the NAS database

### Task 1: Freeze the release source and run the release gate

**Files:**
- Read: `/home/staticduo/git/litellm`
- Create temporarily: `/tmp/litellm-release-8e074a3c6a`
- Read: `/tmp/litellm-release-8e074a3c6a/pyproject.toml`
- Test: `/tmp/litellm-release-8e074a3c6a/tests/test_litellm/proxy/test_component_allowlists.py`
- Test: `/tmp/litellm-release-8e074a3c6a/tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py`
- Test: `/tmp/litellm-release-8e074a3c6a/tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py`
- Test: `/tmp/litellm-release-8e074a3c6a/tests/test_litellm/proxy/common_utils/test_reset_budget_job.py`
- Test: `/tmp/litellm-release-8e074a3c6a/tests/guardrails_tests/test_eu_ai_act_article5.py`

**Interfaces:**
- Consumes: published fork ref `origin/main`
- Produces: clean detached source tree whose `HEAD`, version, and test results are recorded in the release log

- [ ] **Step 1: Re-fetch and prove the release commit is still the published clean `main`**

```bash
cd /home/staticduo/git/litellm
git fetch origin main
git status --porcelain
git rev-parse HEAD
git rev-parse origin/main
git rev-list --left-right --count main...origin/main
git merge-base --is-ancestor upstream/main main
```

Expected: no status output, both SHAs equal `8e074a3c6ac3522a29aaffbc490aa44613c65af8`, divergence is `0 0`, and the ancestry command exits `0`

- [ ] **Step 2: Create an isolated detached release worktree**

```bash
test ! -e /tmp/litellm-release-8e074a3c6a
git worktree add --detach /tmp/litellm-release-8e074a3c6a 8e074a3c6ac3522a29aaffbc490aa44613c65af8
git -C /tmp/litellm-release-8e074a3c6a status --porcelain
git -C /tmp/litellm-release-8e074a3c6a rev-parse HEAD
rg -n '^version = "1.98.0"$' /tmp/litellm-release-8e074a3c6a/pyproject.toml
```

Expected: clean worktree, exact release SHA, and both project version declarations set to `1.98.0`

- [ ] **Step 3: Run focused regression tests for the private behavior retained during the upstream merge**

```bash
cd /tmp/litellm-release-8e074a3c6a
uv run pytest -q \
  tests/test_litellm/proxy/test_component_allowlists.py \
  tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py \
  tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py \
  tests/test_litellm/proxy/common_utils/test_reset_budget_job.py \
  tests/guardrails_tests/test_eu_ai_act_article5.py
```

Expected: all tests pass, covering direct `/lazymcp` gateway routing, scoped LazyMCP resolution, raw-SQL `budget_limits` pagination/reset behavior, and the sentiment guardrail policies

- [ ] **Step 4: Run the repository release gate**

```bash
cd /tmp/litellm-release-8e074a3c6a
make check
```

Expected: exit `0`; retain the log path printed by `make check` in the release record. Stop before building if this gate fails

### Task 2: Capture rollback state and database backups on both hosts

**Files:**
- Create: `/volume2/docker/litellm/releases/20260817-8e074a3c6a/`
- Create on Fedora: `/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/`
- Back up: both `.env`, Compose files, `config.yaml`, `start-litellm.sh`, and `onepassword-mcp-wrapper.sh`

**Interfaces:**
- Consumes: current healthy containers and local PostgreSQL databases
- Produces: two host-specific rollback image tags, two validated PostgreSQL dumps, and sanitized baseline records

- [ ] **Step 1: Create the NAS release state directory and capture configuration without printing it**

```bash
install -d -m 700 /volume2/docker/litellm/releases/20260817-8e074a3c6a
cp -a /volume2/docker/litellm/.env /volume2/docker/litellm/docker-compose.yaml \
  /volume2/docker/litellm/config.yaml /volume2/docker/litellm/start-litellm.sh \
  /volume2/docker/litellm/onepassword-mcp-wrapper.sh \
  /volume2/docker/litellm/releases/20260817-8e074a3c6a/
docker inspect litellm --format '{{.Config.Image}} {{.Image}}' \
  > /volume2/docker/litellm/releases/20260817-8e074a3c6a/previous-image.txt
chmod 600 /volume2/docker/litellm/releases/20260817-8e074a3c6a/*
```

- [ ] **Step 2: Dump and validate the NAS LiteLLM database**

```bash
docker exec postgresql pg_dump -U postgres -d litellm -Fc \
  > /volume2/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
docker exec -i postgresql pg_restore --list \
  < /volume2/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump \
  > /dev/null
test -s /volume2/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
```

Expected: all commands exit `0` and the dump is non-empty

- [ ] **Step 3: Tag and push the exact current NAS image as a rollback artifact**

```bash
docker tag sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa \
  docker.staticduo.com/litellm:rollback-nas-1.92.0-20260817
docker push docker.staticduo.com/litellm:rollback-nas-1.92.0-20260817
```

- [ ] **Step 4: Capture and validate the equivalent Fedora rollback state**

```bash
ssh fedora 'set -euo pipefail
install -d -m 700 /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a
cp -a /home/staticduo/docker/litellm/.env /home/staticduo/docker/litellm/docker-compose.yaml \
  /home/staticduo/docker/litellm/config.yaml /home/staticduo/docker/litellm/start-litellm.sh \
  /home/staticduo/docker/litellm/onepassword-mcp-wrapper.sh \
  /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/
docker inspect litellm --format "{{.Config.Image}} {{.Image}}" \
  > /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/previous-image.txt
docker exec postgresql pg_dump -U postgres -d litellm -Fc \
  > /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
docker exec -i postgresql pg_restore --list \
  < /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump \
  > /dev/null
test -s /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
chmod 600 /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/*
docker tag sha256:dca542cdb661c3c38d029bb960541e10cabc2f33be6baf4259f46b489c32eac3 \
  docker.staticduo.com/litellm:rollback-fedora-1.92.0-20260817
docker push docker.staticduo.com/litellm:rollback-fedora-1.92.0-20260817
'
```

Expected: validated dump and pullable rollback tag exist for Fedora. Stop if either host lacks a usable backup or rollback image

### Task 3: Make both Compose files honor `LITELLM_IMAGE`

**Files:**
- Modify: `/volume2/docker/litellm/docker-compose.yaml:4`
- Modify on Fedora: `/home/staticduo/docker/litellm/docker-compose.yaml:3`
- Modify: `/volume2/docker/litellm/.env:17`
- Modify on Fedora: `/home/staticduo/docker/litellm/.env:17`

**Interfaces:**
- Consumes: current effective local image refs and backed-up Compose files
- Produces: identical image-selection contract on both hosts, `image: "${LITELLM_IMAGE:?LITELLM_IMAGE must be set}"`

- [ ] **Step 1: Normalize NAS Compose without changing the running container**

```bash
sed -i 's|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=litellm:litellm-nas-stream-regression-002|' \
  /volume2/docker/litellm/.env
sed -i 's|^    image: litellm:litellm-nas-stream-regression-002$|    image: "${LITELLM_IMAGE:?LITELLM_IMAGE must be set}"|' \
  /volume2/docker/litellm/docker-compose.yaml
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env config --images | rg -x 'litellm:litellm-nas-stream-regression-002'
docker inspect litellm --format '{{.Config.Image}} {{.State.Status}}'
```

Expected: rendered Compose still names the current NAS image and the existing container remains running

- [ ] **Step 2: Normalize Fedora Compose without changing the running container**

```bash
ssh fedora 'set -euo pipefail
sed -i "s|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=local/litellm-codex-stream:002-9e7a49493b-20260805|" \
  /home/staticduo/docker/litellm/.env
sed -i '\''s|^    image: local/litellm-codex-stream:002-9e7a49493b-20260805$|    image: "${LITELLM_IMAGE:?LITELLM_IMAGE must be set}"|'\'' \
  /home/staticduo/docker/litellm/docker-compose.yaml
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env config --images \
  | rg -x "local/litellm-codex-stream:002-9e7a49493b-20260805"
docker inspect litellm --format "{{.Config.Image}} {{.State.Status}}"
'
```

Expected: rendered Compose still names the current Fedora image and the existing container remains running

### Task 4: Build once, push the immutable tag, and record its digest

**Files:**
- Read: `/tmp/litellm-release-8e074a3c6a/Dockerfile`
- Create: registry manifest for `staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817`
- Create: `/volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt`

**Interfaces:**
- Consumes: gated detached source tree
- Produces: `docker.staticduo.com/litellm@sha256:<digest>` used unchanged by Tasks 5 and 7

- [ ] **Step 1: Build the amd64 image with source labels**

```bash
docker build --pull \
  --label org.opencontainers.image.revision=8e074a3c6ac3522a29aaffbc490aa44613c65af8 \
  --label org.opencontainers.image.version=1.98.0 \
  -t docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817 \
  /tmp/litellm-release-8e074a3c6a
```

Expected: Dockerfile builds the dashboard itself and exits `0`

- [ ] **Step 2: Smoke-test the image before publishing it**

```bash
docker run --rm --entrypoint python \
  docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817 \
  -c 'import importlib.metadata as m; assert m.version("litellm") == "1.98.0"; import litellm.proxy.proxy_server'
docker image inspect \
  docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817 \
  --format '{{.Architecture}} {{index .Config.Labels "org.opencontainers.image.revision"}}'
```

Expected: import succeeds and output is `amd64 8e074a3c6ac3522a29aaffbc490aa44613c65af8`

- [ ] **Step 3: Push only the immutable tag and resolve the registry digest**

```bash
docker push docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817
IMAGE=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.98.0-8e074a3c6a-20260817
DIGEST="$(docker manifest inspect --verbose "$IMAGE" | jq -r '.Descriptor.digest')"
test "${DIGEST#sha256:}" != "$DIGEST"
printf '%s@%s\n' docker.staticduo.com/litellm "$DIGEST" \
  | tee /volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt
```

Expected: `new-image.txt` contains one immutable `repo@sha256:...` reference. Do not create or move `staticduo-gpt-lazymcp-main-latest` yet

### Task 5: Deploy and validate the Fedora canary

**Files:**
- Modify on Fedora: `/home/staticduo/docker/litellm/.env`
- Create on Fedora: `/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-before.json`
- Create on Fedora: `/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-after.json`

**Interfaces:**
- Consumes: immutable image reference from Task 4
- Produces: healthy Fedora canary on LiteLLM `1.98.0` with verified functional behavior

- [ ] **Step 1: Capture Fedora's authenticated model inventory before replacement**

```bash
ssh fedora 'docker exec -i litellm python -' \
  > /tmp/fedora-models-before.json <<'PY'
import json
import os
import urllib.request

request = urllib.request.Request(
    "http://127.0.0.1:4000/v1/models",
    headers={"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    payload = json.load(response)
print(json.dumps(sorted(item["id"] for item in payload["data"]), indent=2))
PY
scp /tmp/fedora-models-before.json \
  fedora:/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-before.json
```

- [ ] **Step 2: Point Fedora at the immutable digest and replace only LiteLLM**

```bash
PINNED_IMAGE="$(cat /volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt)"
ssh fedora "set -euo pipefail
sed -i 's|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=${PINNED_IMAGE}|' /home/staticduo/docker/litellm/.env
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env pull litellm
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env up -d --no-deps litellm
"
```

- [ ] **Step 3: Wait for health and prove version, digest, restarts, and OOM state**

```bash
ssh fedora 'set -euo pipefail
for attempt in $(seq 1 36); do
  health=$(docker inspect litellm --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}")
  test "$health" = healthy && break
  test "$attempt" = 36 && exit 1
  sleep 5
done
docker inspect litellm --format "IMAGE={{.Config.Image}} ID={{.Image}} HEALTH={{.State.Health.Status}} RESTARTS={{.RestartCount}} OOM={{.State.OOMKilled}}"
docker exec litellm python -c '\''import importlib.metadata as m; assert m.version("litellm") == "1.98.0"'\''
'
```

Expected: healthy within 180 seconds, exact `repo@sha256` image ref, version `1.98.0`, zero restarts, and `OOM=false`

- [ ] **Step 4: Run authenticated readiness, model, Responses, and LazyMCP probes**

```bash
MARKER="fedora-release-8e074a3c6a-$(date +%s)"
ssh fedora "docker exec -i -e RELEASE_MARKER=${MARKER} litellm python -" <<'PY'
import json
import os
import urllib.request

base = "http://127.0.0.1:4000"
headers = {
    "Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}",
    "Content-Type": "application/json",
}

def request(path: str, body: dict[str, object] | None = None) -> dict[str, object]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        assert response.status == 200
        return json.load(response)

request("/health/readiness")
models = request("/v1/models")
assert models.get("data")
marker = os.environ["RELEASE_MARKER"]
response = request("/v1/responses", {"model": "gpt-5.6-sol", "input": f"Reply exactly with {marker}"})
assert marker in json.dumps(response)
mcp = request(
    "/v1/responses",
    {
        "model": "gpt-5.6-sol",
        "input": "Use the LazyMCP mcp_status tool and summarize whether the catalog is available",
        "tools": [{
            "type": "mcp",
            "server_label": "lazymcp",
            "server_url": "litellm_proxy/lazymcp",
            "require_approval": "never",
        }],
    },
)
assert any(str(item.get("type", "")).startswith("mcp") for item in mcp.get("output", []))
print(f"fedora-probes=pass marker={marker} models={len(models['data'])}")
PY
```

Expected: valid structured Responses output contains the unique marker and the LazyMCP request performs an MCP interaction. Any replayed/cached response without the marker fails the gate

- [ ] **Step 5: Compare the Fedora model inventory and validate Codex from a fresh process**

```bash
ssh fedora 'docker exec -i litellm python -' \
  > /tmp/fedora-models-after.json <<'PY'
import json
import os
import urllib.request

request = urllib.request.Request(
    "http://127.0.0.1:4000/v1/models",
    headers={"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    payload = json.load(response)
print(json.dumps(sorted(item["id"] for item in payload["data"]), indent=2))
PY
scp /tmp/fedora-models-after.json \
  fedora:/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-after.json
ssh fedora 'diff -u \
  /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-before.json \
  /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/models-after.json'
ssh fedora 'codex doctor'
CODEX_MARKER="fedora-codex-8e074a3c6a-$(date +%s)"
ssh fedora "codex exec -m gpt-5.6-sol 'Return exactly ${CODEX_MARKER}'" | rg -F "$CODEX_MARKER"
```

Expected: no unintended model removals, `codex doctor` passes, and a fresh Codex execution returns the unique marker

### Task 6: Soak Fedora and decide whether NAS promotion is allowed

**Files:**
- Read on Fedora: Docker state and LiteLLM logs since deployment
- Create on Fedora: `/home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/fedora-soak.txt`

**Interfaces:**
- Consumes: validated Fedora canary
- Produces: explicit `PROMOTE` or `ROLLBACK` decision

- [ ] **Step 1: Observe Fedora for 15 minutes without touching NAS**

```bash
SOAK_STARTED_AT="$(date -Is)"
printf 'fedora_soak_started_at=%s\n' "$SOAK_STARTED_AT"
```

Use the session's recurring wait mechanism until 15 minutes have elapsed, yielding an update at least once per minute and making no deployment changes during the interval. Then run:

```bash
ssh fedora 'set -euo pipefail
docker inspect litellm --format "HEALTH={{.State.Health.Status}} RESTARTS={{.RestartCount}} OOM={{.State.OOMKilled}}"
docker logs --since 15m litellm 2>&1 \
  | rg -i "traceback|unhandled|prisma.*error|migration.*error|mcp.*error|5[0-9][0-9]" \
  > /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/fedora-soak.txt || true
wc -l /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/fedora-soak.txt
'
```

- [ ] **Step 2: Apply the promotion gate**

Promote only if Fedora remains healthy with zero restarts and no OOM, model inventory is acceptable, Responses and LazyMCP probes pass, Codex returns its unique marker, and every matched soak log line has been reviewed as benign. Otherwise execute Task 9 for Fedora and stop the release before NAS

### Task 7: Promote the exact Fedora-tested digest to NAS

**Files:**
- Modify: `/volume2/docker/litellm/.env`
- Create: `/volume2/docker/litellm/releases/20260817-8e074a3c6a/models-before.json`
- Create: `/volume2/docker/litellm/releases/20260817-8e074a3c6a/models-after.json`

**Interfaces:**
- Consumes: the same immutable digest accepted on Fedora
- Produces: healthy NAS deployment on LiteLLM `1.98.0`

- [ ] **Step 1: Capture NAS's authenticated model inventory**

```bash
docker exec -i litellm python - \
  > /volume2/docker/litellm/releases/20260817-8e074a3c6a/models-before.json <<'PY'
import json
import os
import urllib.request

request = urllib.request.Request(
    "http://127.0.0.1:4000/v1/models",
    headers={"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    payload = json.load(response)
print(json.dumps(sorted(item["id"] for item in payload["data"]), indent=2))
PY
```

- [ ] **Step 2: Deploy the exact pinned digest to NAS**

```bash
PINNED_IMAGE="$(cat /volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt)"
sed -i "s|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=${PINNED_IMAGE}|" /volume2/docker/litellm/.env
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env pull litellm
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env up -d --no-deps litellm
```

- [ ] **Step 3: Validate NAS health, version, digest, models, Responses, LazyMCP, and logs**

```bash
for attempt in $(seq 1 36); do
  health=$(docker inspect litellm --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}')
  test "$health" = healthy && break
  test "$attempt" = 36 && exit 1
  sleep 5
done
docker inspect litellm --format 'IMAGE={{.Config.Image}} ID={{.Image}} HEALTH={{.State.Health.Status}} RESTARTS={{.RestartCount}} OOM={{.State.OOMKilled}}'
docker exec litellm python -c 'import importlib.metadata as m; assert m.version("litellm") == "1.98.0"'
NAS_MARKER="nas-release-8e074a3c6a-$(date +%s)"
docker exec -i -e RELEASE_MARKER="$NAS_MARKER" litellm python - <<'PY'
import json
import os
import urllib.request

headers = {
    "Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}",
    "Content-Type": "application/json",
}

def request(path: str, body: dict[str, object] | None = None) -> dict[str, object]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request("http://127.0.0.1:4000" + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        assert response.status == 200
        return json.load(response)

request("/health/readiness")
models = request("/v1/models")
assert models.get("data")
marker = os.environ["RELEASE_MARKER"]
response = request("/v1/responses", {"model": "gpt-5.6-sol", "input": f"Reply exactly with {marker}"})
assert marker in json.dumps(response)
mcp = request(
    "/v1/responses",
    {
        "model": "gpt-5.6-sol",
        "input": "Use the LazyMCP mcp_status tool and summarize whether the catalog is available",
        "tools": [{
            "type": "mcp",
            "server_label": "lazymcp",
            "server_url": "litellm_proxy/lazymcp",
            "require_approval": "never",
        }],
    },
)
assert any(str(item.get("type", "")).startswith("mcp") for item in mcp.get("output", []))
print(f"nas-probes=pass marker={marker} models={len(models['data'])}")
PY
docker exec -i litellm python - \
  > /volume2/docker/litellm/releases/20260817-8e074a3c6a/models-after.json <<'PY'
import json
import os
import urllib.request

request = urllib.request.Request(
    "http://127.0.0.1:4000/v1/models",
    headers={"Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    payload = json.load(response)
print(json.dumps(sorted(item["id"] for item in payload["data"]), indent=2))
PY
diff -u \
  /volume2/docker/litellm/releases/20260817-8e074a3c6a/models-before.json \
  /volume2/docker/litellm/releases/20260817-8e074a3c6a/models-after.json
docker logs --since 10m litellm 2>&1 \
  | rg -i 'traceback|unhandled|prisma.*error|migration.*error|mcp.*error|5[0-9][0-9]' || true
```

Expected: NAS is healthy on `1.98.0`, uses the exact digest stored in `new-image.txt`, retains its intended model inventory, returns the unique Responses marker, completes the LazyMCP interaction, and has zero restarts and no OOM

- [ ] **Step 4: Validate both public NAS routes with authenticated unique markers**

```bash
for PUBLIC_BASE in https://litellm.staticduo.com https://litellm.defend.tech; do
  PUBLIC_BASE="$PUBLIC_BASE" RELEASE_MARKER="public-8e074a3c6a-$(date +%s)-$(basename "$PUBLIC_BASE")" \
    docker exec -i -e PUBLIC_BASE -e RELEASE_MARKER litellm python - <<'PY'
import json
import os
import urllib.request

marker = os.environ["RELEASE_MARKER"]
request = urllib.request.Request(
    os.environ["PUBLIC_BASE"] + "/v1/responses",
    data=json.dumps({"model": "gpt-5.6-sol", "input": f"Reply exactly with {marker}"}).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}",
        "Content-Type": "application/json",
    },
)
with urllib.request.urlopen(request, timeout=180) as response:
    payload = json.load(response)
assert marker in json.dumps(payload)
print(f"public-route=pass marker={marker}")
PY
done
```

- [ ] **Step 5: Validate Codex on NAS**

```bash
codex doctor
CODEX_MARKER="nas-codex-8e074a3c6a-$(date +%s)"
codex exec -m gpt-5.6-sol "Return exactly ${CODEX_MARKER}" | rg -F "$CODEX_MARKER"
```

### Task 8: Promote stable and close the release

**Files:**
- Create: registry tag `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest`
- Create: `/volume2/docker/litellm/releases/20260817-8e074a3c6a/release-result.txt`

**Interfaces:**
- Consumes: successful Fedora and NAS validation
- Produces: stable tag pointing to released content and a complete release record

- [ ] **Step 1: Move stable only after both hosts pass**

```bash
PINNED_IMAGE="$(cat /volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt)"
docker pull "$PINNED_IMAGE"
docker tag "$PINNED_IMAGE" docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest
docker push docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest
EXPECTED_DIGEST="${PINNED_IMAGE##*@}"
STABLE_DIGEST="$(docker manifest inspect --verbose \
  docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest \
  | jq -r '.Descriptor.digest')"
test "$STABLE_DIGEST" = "$EXPECTED_DIGEST"
```

- [ ] **Step 2: Prove both containers execute the same content digest**

```bash
docker inspect litellm --format '{{.Config.Image}} {{.Image}}'
ssh fedora 'docker inspect litellm --format "{{.Config.Image}} {{.Image}}"'
```

Expected: both `Config.Image` values equal `new-image.txt` and both runtime image IDs are identical

- [ ] **Step 3: Record the release facts without secrets**

```bash
{
  printf 'source_sha=%s\n' 8e074a3c6ac3522a29aaffbc490aa44613c65af8
  printf 'version=%s\n' 1.98.0
  printf 'image=%s\n' "$(cat /volume2/docker/litellm/releases/20260817-8e074a3c6a/new-image.txt)"
  printf 'fedora_previous=%s\n' docker.staticduo.com/litellm:rollback-fedora-1.92.0-20260817
  printf 'nas_previous=%s\n' docker.staticduo.com/litellm:rollback-nas-1.92.0-20260817
  printf 'fedora_result=pass\n'
  printf 'nas_result=pass\n'
} > /volume2/docker/litellm/releases/20260817-8e074a3c6a/release-result.txt
chmod 600 /volume2/docker/litellm/releases/20260817-8e074a3c6a/release-result.txt
```

- [ ] **Step 4: Retain rollback artifacts for seven days**

Do not delete either `1.92.0` rollback tag, either database dump, or either host configuration backup before `2026-08-24`. Do not prune the previous local image IDs during this window

- [ ] **Step 5: Remove only the temporary detached source worktree**

```bash
git -C /home/staticduo/git/litellm worktree remove /tmp/litellm-release-8e074a3c6a
git -C /home/staticduo/git/litellm worktree prune
```

### Task 9: Rollback runbook

**Files:**
- Restore from the host-specific `releases/20260817-8e074a3c6a/` directory
- Modify only the failed host's `.env` and LiteLLM container unless database evidence requires a restore

**Interfaces:**
- Consumes: rollback image and backups from Task 2
- Produces: failed host restored to its observed LiteLLM `1.92.0` state

- [ ] **Step 1: Roll back Fedora immediately if the canary fails**

```bash
ssh fedora 'set -euo pipefail
sed -i "s|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=docker.staticduo.com/litellm:rollback-fedora-1.92.0-20260817|" \
  /home/staticduo/docker/litellm/.env
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env pull litellm
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env up -d --no-deps litellm
'
```

Proceed to Step 4 with `VERIFY_HOST=fedora`. NAS remains untouched

- [ ] **Step 2: Roll back NAS if NAS promotion fails after Fedora passed**

```bash
sed -i 's|^LITELLM_IMAGE=.*$|LITELLM_IMAGE=docker.staticduo.com/litellm:rollback-nas-1.92.0-20260817|' \
  /volume2/docker/litellm/.env
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env pull litellm
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env up -d --no-deps litellm
```

Proceed to Step 4 with `VERIFY_HOST=nas`. Fedora may remain on `1.98.0` while the NAS fault is investigated because the databases are independent

- [ ] **Step 3: Restore a database only if application rollback fails due to a proven incompatible migration**

First stop request traffic to the affected host and record the exact rollback time. Restoring the dump destroys all writes made after Task 2, so this step requires an explicit go/no-go decision based on logs and schema errors

Fedora destructive restore command:

```bash
ssh fedora 'set -euo pipefail
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env stop litellm
docker exec -i postgresql pg_restore -U postgres -d litellm --clean --if-exists \
  < /home/staticduo/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
docker compose -f /home/staticduo/docker/litellm/docker-compose.yaml \
  --env-file /home/staticduo/docker/litellm/.env up -d --no-deps litellm
'
```

NAS destructive restore command:

```bash
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env stop litellm
docker exec -i postgresql pg_restore -U postgres -d litellm --clean --if-exists \
  < /volume2/docker/litellm/releases/20260817-8e074a3c6a/litellm.pgdump
docker compose -f /volume2/docker/litellm/docker-compose.yaml \
  --env-file /volume2/docker/litellm/.env up -d --no-deps litellm
```

After either database restore, run Step 4 for the restored host and keep the stable tag on the last release that passed both hosts

- [ ] **Step 4: Prove the selected host recovered completely**

Set `VERIFY_HOST=fedora` for a failed canary or `VERIFY_HOST=nas` for a failed NAS promotion:

```bash
VERIFY_HOST=fedora
ROLLBACK_MARKER="rollback-${VERIFY_HOST}-1.92.0-$(date +%s)"
ssh "$VERIFY_HOST" "docker exec -i -e RELEASE_MARKER=${ROLLBACK_MARKER} litellm python -" <<'PY'
import importlib.metadata
import json
import os
import urllib.request

assert importlib.metadata.version("litellm") == "1.92.0"
headers = {
    "Authorization": f"Bearer {os.environ['LITELLM_MASTER_KEY']}",
    "Content-Type": "application/json",
}

def request(path: str, body: dict[str, object] | None = None) -> dict[str, object]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request("http://127.0.0.1:4000" + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        assert response.status == 200
        return json.load(response)

request("/health/readiness")
models = request("/v1/models")
assert models.get("data")
marker = os.environ["RELEASE_MARKER"]
response = request("/v1/responses", {"model": "gpt-5.6-sol", "input": f"Reply exactly with {marker}"})
assert marker in json.dumps(response)
mcp = request(
    "/v1/responses",
    {
        "model": "gpt-5.6-sol",
        "input": "Use the LazyMCP mcp_status tool and summarize whether the catalog is available",
        "tools": [{
            "type": "mcp",
            "server_label": "lazymcp",
            "server_url": "litellm_proxy/lazymcp",
            "require_approval": "never",
        }],
    },
)
assert any(str(item.get("type", "")).startswith("mcp") for item in mcp.get("output", []))
print(f"rollback-probes=pass marker={marker} models={len(models['data'])}")
PY
ssh "$VERIFY_HOST" 'docker inspect litellm --format "HEALTH={{.State.Health.Status}} RESTARTS={{.RestartCount}} OOM={{.State.OOMKilled}}"'
ssh "$VERIFY_HOST" 'codex doctor'
ssh "$VERIFY_HOST" "codex exec -m gpt-5.6-sol 'Return exactly ${ROLLBACK_MARKER}'" | rg -F "$ROLLBACK_MARKER"
ssh "$VERIFY_HOST" 'docker logs --since 10m litellm 2>&1' \
  | rg -i 'traceback|unhandled|prisma.*error|migration.*error|mcp.*error|5[0-9][0-9]' || true
```

Expected: version is back to `1.92.0`, all authenticated probes and Codex pass, the container is healthy with no OOM, and every matched log line is reviewed before declaring recovery

## Post-Release Follow-Up

The existing `/home/staticduo/git/release-litellm.sh` should be replaced or refactored in a separate change before the next release. That change should split `prepare`, `build`, `deploy-fedora`, `promote-nas`, `promote-stable`, and `rollback` into explicit phases; discover current images on both hosts; back up both databases and configurations; deploy by digest; validate after each host; and default to Fedora-first. Its current mode `777` should also be reduced to `750` or `700`
