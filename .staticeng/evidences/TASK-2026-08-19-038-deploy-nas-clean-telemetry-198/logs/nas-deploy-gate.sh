#!/usr/bin/env bash
set -Eeuo pipefail

readonly STACK=/volume2/docker/litellm
readonly CANDIDATE_REF=docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly CANDIDATE_MANIFEST=sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly CANDIDATE_CONFIG=sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a
readonly CANDIDATE_REVISION=177c66ef727710a455f058b99f653df9b3e4c0a4
readonly RELEASE_ROOT="$STACK/releases/20260819-clean-telemetry-198-deploy"
readonly ATTEMPT_ID="nas-clean-$(date -u +%Y%m%dT%H%M%SZ)"
readonly ATTEMPT="$RELEASE_ROOT/attempts/$ATTEMPT_ID"
readonly ROLLBACK="$RELEASE_ROOT/rollback-$ATTEMPT_ID"
readonly COMPOSE="$STACK/docker-compose.yaml"
readonly ENV_FILE="$STACK/.env"
readonly FEDORA_BASE="$ATTEMPT/fedora-baseline.txt"
readonly STABLE_BASE="$ATTEMPT/stable-baseline.txt"
readonly FEDORA_HOST=staticduo@fedora-ssh.staticduo.com
readonly FEDORA_KNOWN_HOSTS=/home/staticduo/.ssh/known_hosts
readonly FEDORA_IDENTITY=/home/staticduo/.ssh/id_rsa

DEPLOYED=false
ACCEPTED=false

atomic_write() {
  local path=$1
  local tmp="${path}.tmp.$$"
  cat >"$tmp"
  chmod 600 "$tmp"
  chown root:root "$tmp"
  sync "$tmp"
  mv -f "$tmp" "$path"
  sync "$(dirname "$path")"
}

record() {
  local gate=$1
  local status=$2
  local expected=$3
  local actual=$4
  local artifact=$5
  local artifact_hash
  artifact_hash=$(sha256sum "$artifact" | cut -d' ' -f1)
  jq -n \
    --arg attempt "$ATTEMPT_ID" \
    --arg gate "$gate" \
    --arg status "$status" \
    --arg expected "$expected" \
    --arg actual "$actual" \
    --arg container "$(docker inspect -f '{{.Id}}' litellm 2>/dev/null || true)" \
    --arg artifact "$(basename "$artifact")" \
    --arg hash "$artifact_hash" \
    --arg timestamp "$(date -u +%FT%TZ)" \
    '{attempt:$attempt,gate:$gate,status:$status,expected:$expected,actual:$actual,container_identity:$container,artifact:$artifact,artifact_sha256:$hash,persisted_at:$timestamp}' \
    | atomic_write "$ATTEMPT/${gate}.result.json"
  test "$status" = PASS
}

fedora_projection() {
  ssh -o BatchMode=yes -o RequestTTY=no -o StrictHostKeyChecking=yes -o ClearAllForwardings=yes \
    -o IdentitiesOnly=yes -o UserKnownHostsFile="$FEDORA_KNOWN_HOSTS" -i "$FEDORA_IDENTITY" "$FEDORA_HOST" '
      set -eu
      test "$(id -un)" = staticduo
      test "$(id -u)" = 1000
      docker inspect litellm
    ' | python3 -c '
import json
import sys

item = json.load(sys.stdin)[0]
health = (item["State"].get("Health") or {}).get("Status", "")
mounts = sorted((entry["Source"], entry["Destination"], entry["Type"], entry["RW"]) for entry in item["Mounts"])
networks = sorted((name, value["NetworkID"]) for name, value in item["NetworkSettings"]["Networks"].items())
print(json.dumps({"user":"staticduo","uid":1000,"container":item["Id"],"image":item["Image"],"image_ref":item["Config"]["Image"],"status":item["State"]["Status"],"health":health,"restarts":item["RestartCount"],"oom":item["State"]["OOMKilled"],"started":item["State"]["StartedAt"],"mounts":mounts,"networks":networks},sort_keys=True,separators=(",",":")))
'
}

rollback() {
  set +e
  if test "$DEPLOYED" = true && test "$ACCEPTED" != true; then
    cp "$ROLLBACK/.env" "$ENV_FILE"
    cp "$ROLLBACK/docker-compose.yaml" "$COMPOSE"
    cp "$ROLLBACK/start-litellm.sh" "$STACK/start-litellm.sh"
    cp "$ROLLBACK/onepassword-mcp-wrapper.sh" "$STACK/onepassword-mcp-wrapper.sh"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE" up -d --no-deps litellm
    for _ in $(seq 1 60); do
      test "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' litellm 2>/dev/null)" = healthy && break
      sleep 2
    done
    docker inspect -f '{{.Id}}|{{.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}' litellm \
      | atomic_write "$ATTEMPT/rollback-final.txt"
  fi
}
trap rollback EXIT

install -d -o root -g root -m 700 "$RELEASE_ROOT" "$RELEASE_ROOT/attempts" "$ATTEMPT" "$ROLLBACK"
cp -a "$ENV_FILE" "$ROLLBACK/.env"
cp -a "$COMPOSE" "$ROLLBACK/docker-compose.yaml"
cp -a "$STACK/start-litellm.sh" "$ROLLBACK/start-litellm.sh"
cp -a "$STACK/onepassword-mcp-wrapper.sh" "$ROLLBACK/onepassword-mcp-wrapper.sh"
  chmod 600 "$ROLLBACK"/* "$ROLLBACK/.env"
  chown root:root "$ROLLBACK"/* "$ROLLBACK/.env"

docker inspect -f '{{.Id}}|{{.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/nas-container-baseline.txt"
docker ps --format '{{.Names}}|{{.ID}}' | sort | atomic_write "$ATTEMPT/nas-containers-baseline.txt"
docker inspect -f '{{range .Mounts}}{{println .Source "|" .Destination "|" .Type "|" .RW}}{{end}}{{range $k,$v := .NetworkSettings.Networks}}{{println $k "|" $v.NetworkID}}{{end}}' litellm \
  | sort | atomic_write "$ATTEMPT/nas-runtime-baseline.txt"
grep -Fx '/volume2/docker/litellm/data/op_service_account_token | /run/secrets/op_service_account_token | bind | false' "$ATTEMPT/nas-runtime-baseline.txt" >/dev/null
python3 - "$ENV_FILE" >"$ATTEMPT/non-image-env-baseline.sha256" <<'PY'
import hashlib
import sys
from pathlib import Path

lines = [line for line in Path(sys.argv[1]).read_text().splitlines() if not line.startswith("LITELLM_IMAGE=")]
print(hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest())
PY
chmod 600 "$ATTEMPT/non-image-env-baseline.sha256"
chown root:root "$ATTEMPT/non-image-env-baseline.sha256"
sha256sum "$COMPOSE" "$STACK/config.yaml" "$STACK/start-litellm.sh" "$STACK/onepassword-mcp-wrapper.sh" \
  | atomic_write "$ATTEMPT/protected-baseline.sha256"
python3 - "$STACK/data/op_service_account_token" >"$ATTEMPT/service-account-directory-baseline.json" <<'PY'
import hashlib
import json
import stat
import sys
from pathlib import Path

path = Path(sys.argv[1])
info = path.lstat()
if path.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o755:
    raise SystemExit("unsafe service-account mount source")
children = sorted(path.iterdir())
if children:
    raise SystemExit("service-account mount source is not empty")
print(json.dumps({"type":"directory","uid":info.st_uid,"gid":info.st_gid,"mode":stat.S_IMODE(info.st_mode),"size":info.st_size,"mtime_ns":info.st_mtime_ns,"ctime_ns":info.st_ctime_ns,"inode":info.st_ino,"device":info.st_dev,"direct_child_projection_sha256":hashlib.sha256(b"[]").hexdigest()},sort_keys=True,separators=(",",":")))
PY
chmod 600 "$ATTEMPT/service-account-directory-baseline.json"
chown root:root "$ATTEMPT/service-account-directory-baseline.json"
docker inspect -f '{{.Name}}|{{.Id}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat \
  | sort | atomic_write "$ATTEMPT/dependencies-baseline.txt"

python3 - "$STACK/data" >"$ATTEMPT/credentials-baseline.tsv" <<'PY'
import hashlib
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
for profile in ("chatgpt-auth", "anthropic-auth"):
    directory = root / profile
    if directory.is_symlink() or directory.resolve() != directory:
        raise SystemExit("unsafe credential root")
    for path in (directory, *sorted(directory.iterdir())):
        info = path.lstat()
        kind = "d" if stat.S_ISDIR(info.st_mode) else "f" if stat.S_ISREG(info.st_mode) else "other"
        label = "ROOT" if path == directory else hashlib.sha256(path.name.encode()).hexdigest()
        category = "root" if path == directory else "lock" if info.st_size == 0 else "credential"
        print("\t".join(map(str, (profile, label, category, kind, info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode), info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino, info.st_dev))))
PY
chmod 600 "$ATTEMPT/credentials-baseline.tsv"
chown root:root "$ATTEMPT/credentials-baseline.tsv"
python3 - "$ATTEMPT/credentials-baseline.tsv" <<'PY'
import sys
from pathlib import Path

for line in Path(sys.argv[1]).read_text().splitlines():
    profile, label, category, kind, uid, gid, mode, size, *_ = line.split("\t")
    expected_mode = "448" if category == "root" else "384"
    if kind not in {"d" if category == "root" else "f"} or uid != "0" or gid != "0" or mode != expected_mode:
        raise SystemExit(f"unsafe credential metadata: {profile}/{label}")
    if category == "lock" and size != "0":
        raise SystemExit("non-empty credential lock")
PY

docker logs --since 15m litellm 2>&1 | python3 -c 'import re,sys; text=sys.stdin.read(); patterns=(r"Authentication required",r"device flow",r"device_auth",r"auth\.openai",r"login\.openai"); count=sum(len(re.findall(p,text,re.I)) for p in patterns); print(f"auth_device_markers={count}"); raise SystemExit(count != 0)' \
  | atomic_write "$ATTEMPT/preflight-auth-log.txt"

docker exec -i litellm python - >"$ATTEMPT/topology-baseline.json" <<'PY'
import hashlib
import json
import os
import urllib.request

def get(path):
    request = urllib.request.Request("http://127.0.0.1:4000" + path, headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]})
    return json.loads(urllib.request.urlopen(request, timeout=30).read())

models = get("/model/info")["data"]
settings = get("/router/settings")["current_values"]
projection = sorted((row["model_name"], row.get("model_info", {}).get("id", "")) for row in models)
fallbacks = settings.get("fallbacks") or []
names = [name for name, _ in projection]
result = {
    "rows": len(projection),
    "projection_sha256": hashlib.sha256(json.dumps(projection, separators=(",", ":")).encode()).hexdigest(),
    "fallbacks": len(fallbacks),
    "fallbacks_sha256": hashlib.sha256(json.dumps(fallbacks, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    "default_qualified": sum(name.startswith("chatgpt/") for name in names),
    "account2_qualified": sum(name.startswith("chatgpt-account2/") for name in names),
    "account3": sum("account3" in name for name in names) + sum("account3" in json.dumps(item) for item in fallbacks),
    "cross_profile": settings.get("allow_chatgpt_cross_profile_fallback"),
}
print(json.dumps(result, sort_keys=True))
PY
chmod 600 "$ATTEMPT/topology-baseline.json"
chown root:root "$ATTEMPT/topology-baseline.json"
jq -e '.rows == 32 and .fallbacks == 16 and .default_qualified == 8 and .account2_qualified == 8 and .account3 == 0 and .cross_profile == true' "$ATTEMPT/topology-baseline.json" >/dev/null

fedora_projection | atomic_write "$FEDORA_BASE"
jq -e --arg manifest "$CANDIDATE_MANIFEST" '.user == "staticduo" and .uid == 1000 and .image == $manifest and .image_ref == ("docker.staticduo.com/litellm@" + $manifest) and .status == "running" and .health == "healthy" and .restarts == 0 and .oom == false' "$FEDORA_BASE" >/dev/null
if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$STABLE_BASE.tmp" 2>/dev/null; then
  jq -r '.digest // .Digest' "$STABLE_BASE.tmp" | atomic_write "$STABLE_BASE"
else
  printf 'MISSING\n' | atomic_write "$STABLE_BASE"
fi
rm -f "$STABLE_BASE.tmp"

python3 - <<'PY'
import os
import stat
from pathlib import Path

checks = (
    (Path("/home/staticduo/.docker"), 1000, 10, 0o700, "directory"),
    (Path("/home/staticduo/.docker/config.json"), 1000, 10, 0o600, "file"),
    (Path("/root/.docker"), 0, 0, 0o700, "directory"),
    (Path("/root/.docker/config.json"), 0, 0, 0o600, "file"),
)
for path, uid, gid, mode, kind in checks:
    info = path.lstat()
    valid_kind = stat.S_ISDIR(info.st_mode) if kind == "directory" else stat.S_ISREG(info.st_mode)
    if path.is_symlink() or not valid_kind or info.st_uid != uid or info.st_gid != gid or stat.S_IMODE(info.st_mode) != mode:
        raise SystemExit(f"unsafe Docker credential metadata: {path}")
PY
docker info --format '{{.ID}}' >"$ATTEMPT/root-daemon-id.txt"
sudo -u staticduo docker info --format '{{.ID}}' >"$ATTEMPT/staticduo-daemon-id.txt"
chmod 600 "$ATTEMPT/root-daemon-id.txt" "$ATTEMPT/staticduo-daemon-id.txt"
chown root:root "$ATTEMPT/root-daemon-id.txt" "$ATTEMPT/staticduo-daemon-id.txt"
cmp -s "$ATTEMPT/root-daemon-id.txt" "$ATTEMPT/staticduo-daemon-id.txt"
docker image inspect -f '{{.Id}}|{{json .RepoDigests}}|{{index .Config.Labels "org.opencontainers.image.version"}}|{{index .Config.Labels "org.opencontainers.image.revision"}}|{{.Architecture}}' "$CANDIDATE_REF" \
  | atomic_write "$ATTEMPT/candidate-root-identity.txt"
sudo -u staticduo docker image inspect -f '{{.Id}}|{{json .RepoDigests}}|{{index .Config.Labels "org.opencontainers.image.version"}}|{{index .Config.Labels "org.opencontainers.image.revision"}}|{{.Architecture}}' "$CANDIDATE_REF" \
  | atomic_write "$ATTEMPT/candidate-staticduo-identity.txt"
cmp -s "$ATTEMPT/candidate-root-identity.txt" "$ATTEMPT/candidate-staticduo-identity.txt"
cp "$ATTEMPT/candidate-root-identity.txt" "$ATTEMPT/candidate-preflight.txt"
chmod 600 "$ATTEMPT/candidate-preflight.txt"
chown root:root "$ATTEMPT/candidate-preflight.txt"
test "$(docker image inspect -f '{{.Id}}' "$CANDIDATE_REF")" = "$CANDIDATE_CONFIG"
grep -q "$CANDIDATE_MANIFEST" "$ATTEMPT/candidate-preflight.txt"
grep -q "1.98.0|$CANDIDATE_REVISION|amd64" "$ATTEMPT/candidate-preflight.txt"
record preflight PASS 'strict baseline, rollback, candidate, credentials, topology, Fedora and stable' 'all preflight predicates passed' "$ATTEMPT/candidate-preflight.txt"

python3 - "$ENV_FILE" "$CANDIDATE_REF" <<'PY'
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
candidate = sys.argv[2]
lines = path.read_text().splitlines()
matches = [index for index, line in enumerate(lines) if line.startswith("LITELLM_IMAGE=")]
if len(matches) != 1:
    raise SystemExit("expected exactly one LITELLM_IMAGE")
lines[matches[0]] = "LITELLM_IMAGE=" + candidate
temporary = path.with_name(path.name + ".candidate")
temporary.write_text("\n".join(lines) + "\n")
os.chmod(temporary, path.stat().st_mode & 0o777)
os.replace(temporary, path)
PY
DEPLOYED=true
docker compose --env-file "$ENV_FILE" -f "$COMPOSE" up -d --no-deps litellm >/dev/null
for _ in $(seq 1 90); do
  test "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' litellm)" = healthy && break
  sleep 2
done
test "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' litellm)" = healthy
readonly CANDIDATE_CONTAINER=$(docker inspect -f '{{.Id}}' litellm)
readonly CANDIDATE_STARTED=$(docker inspect -f '{{.State.StartedAt}}' litellm)
docker inspect -f '{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/deployment-identity.txt"
grep -q "|$CANDIDATE_CONFIG|$CANDIDATE_REF|running|healthy|0|false|" "$ATTEMPT/deployment-identity.txt"
record deployment_identity PASS "$CANDIDATE_MANIFEST / $CANDIDATE_CONFIG / healthy" 'only NAS LiteLLM recreated by --no-deps' "$ATTEMPT/deployment-identity.txt"

docker exec -i litellm python - >"$ATTEMPT/functional.json" <<'PY'
import json
import os
import urllib.error
import urllib.request

base = "http://127.0.0.1:4000"
headers = {"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"], "Content-Type": "application/json", "x-openai-internal-codex-responses-lite": "true"}

def get(path):
    request = urllib.request.Request(base + path, headers=headers)
    return json.loads(urllib.request.urlopen(request, timeout=30).read())

rows = get("/model/info")["data"]
ids = {row["model_name"]: row.get("model_info", {}).get("id", "") for row in rows}
default_id = ids["chatgpt/gpt-5.6-sol"]
account2_id = ids["chatgpt-account2/gpt-5.6-sol"]

def probe(label, model, stream, expected_id, allow_quota=False):
    payload = json.dumps({
        "model": model,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": "Reply with exactly OK."}]}],
        "reasoning": {"context": "all_turns", "effort": "high", "summary": "detailed"},
        "stream": stream,
        "store": False,
        "include": ["reasoning.encrypted_content"],
        "parallel_tool_calls": False,
    }).encode()
    request = urllib.request.Request(base + "/v1/responses", data=payload, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=180)
        status, response_headers, body = response.status, response.headers, response.read().decode(errors="replace")
    except urllib.error.HTTPError as error:
        status, response_headers, body = error.code, error.headers, error.read().decode(errors="replace")
    selected = response_headers.get("x-litellm-model-id", "")
    blocked = ("Stream must be set to true", "Authentication required", "device flow", "unsupported_value", "unsupported_model", "response.failed")
    if selected != expected_id or any(marker.lower() in body.lower() for marker in blocked):
        raise SystemExit(label + " selection or blocked-error failure")
    if status == 429 and allow_quota:
        if not any(marker in body.lower() for marker in ("quota", "rate", "429", "too many")):
            raise SystemExit(label + " unclassified 429")
        return {"label": label, "status": status, "classification": "provider_quota", "selected_expected": True}
    if status != 200 or not response_headers.get_content_type().startswith("text/event-stream"):
        raise SystemExit(label + " expected HTTP 200 SSE")
    events = []
    for record in body.replace("\r\n", "\n").split("\n\n"):
        data = "\n".join(line[5:].strip() for line in record.splitlines() if line.startswith("data:"))
        if data and data != "[DONE]":
            events.append(json.loads(data))
    types = [event.get("type") for event in events]
    if types.count("response.completed") != 1 or "response.created" not in types or "response.in_progress" not in types:
        raise SystemExit(label + " invalid SSE lifecycle")
    if types.index("response.created") > types.index("response.in_progress") or types.index("response.in_progress") > types.index("response.completed"):
        raise SystemExit(label + " unordered SSE lifecycle")
    if types[-1] != "response.completed":
        raise SystemExit(label + " post-completion event")
    return {"label": label, "status": status, "classification": "completed_sse", "events": len(events), "selected_expected": True}

results = [
    probe("native_stream_false", "chatgpt/gpt-5.6-sol", False, default_id),
    probe("direct_default", "chatgpt/gpt-5.6-sol", True, default_id),
    probe("direct_account2", "chatgpt-account2/gpt-5.6-sol", True, account2_id, True),
    probe("public_default_primary", "gpt-5.6-sol", True, default_id),
]
print(json.dumps(results, sort_keys=True))
PY
chmod 600 "$ATTEMPT/functional.json"
chown root:root "$ATTEMPT/functional.json"
record functional PASS 'native/default/public HTTP 200 SSE; account2 HTTP 200 SSE or provider quota 429' 'all four corrected Responses/Codex gates passed' "$ATTEMPT/functional.json"

docker exec -i litellm python - >"$ATTEMPT/lazymcp.json" <<'PY'
import json
import os
import urllib.request

url = "http://127.0.0.1:4000/lazymcp"
headers = {"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"], "Content-Type": "application/json", "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-11-25"}

def call(identifier, method, params):
    request = urllib.request.Request(url, data=json.dumps({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params}).encode(), headers=headers)
    raw = urllib.request.urlopen(request, timeout=120).read().decode()
    lines = [line.removeprefix("data:").strip() for line in raw.splitlines() if line.startswith("data:")]
    result = json.loads(lines[-1] if lines else raw)
    if result.get("error") or result.get("result", {}).get("isError") is True:
        raise SystemExit("LazyMCP call failed")
    return result

listed = call(1, "tools/list", {})
names = sorted(tool["name"] for tool in listed["result"]["tools"])
if names != ["mcp_call", "mcp_describe", "mcp_status"]:
    raise SystemExit("unexpected LazyMCP tools")
call(2, "tools/call", {"name": "mcp_status", "arguments": {}})
described = call(3, "tools/call", {"name": "mcp_describe", "arguments": {"server": "defend_memory", "tool": "defend_memory-find"}})
if "defend_memory-find" not in json.dumps(described):
    raise SystemExit("LazyMCP describe mismatch")
call(4, "tools/call", {"name": "mcp_call", "arguments": {"server": "defend_memory", "tool": "defend_memory-find", "arguments": {"query": "TASK-2026-08-19-038 harmless validation"}}})
print(json.dumps({"protocol": "2025-11-25", "tools": names, "status": "pass", "describe": "pass", "call": "pass"}, sort_keys=True))
PY
chmod 600 "$ATTEMPT/lazymcp.json"
chown root:root "$ATTEMPT/lazymcp.json"
record lazymcp PASS 'status, exact tool list, describe, harmless call' 'full LazyMCP matrix passed' "$ATTEMPT/lazymcp.json"

for poll in $(seq 1 21); do
  test "$(docker inspect -f '{{.Id}}' litellm)" = "$CANDIDATE_CONTAINER"
  docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}" litellm
  docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}" litellm-redis
  if test "$poll" -lt 21; then sleep 30; fi
done | atomic_write "$ATTEMPT/observation-polls.txt"

docker logs --since "$CANDIDATE_STARTED" litellm 2>&1 | python3 -c '
import json
import re
import sys
text = sys.stdin.read()
patterns = {
    "standard_logging": r"standard_logging_object.*(?:missing|invalid)|StandardLoggingPayload.*(?:missing|invalid)|success callback.*(?:error|traceback)|success handler.*traceback",
    "usage_cache": r"resolved_usage_cache.*(?:NameError|not defined)|NameError.*resolved_usage_cache|cache.settings.*(?:error|traceback)",
    "stream": r"Stream must be set to true|response.failed",
    "auth_device": r"Authentication required|device flow|device_auth|auth\\.openai|login\\.openai",
    "migration_schema_patch": r"migration.*(?:error|failed)|schema.*(?:error|failed)|patch.*(?:error|failed)",
    "traceback": r"Traceback \(most recent call last\)",
}
counts = {name: len(re.findall(pattern, text, re.I)) for name, pattern in patterns.items()}
print(json.dumps(counts, sort_keys=True))
raise SystemExit(any(counts.values()))
' | atomic_write "$ATTEMPT/candidate-log-summary.json"
record observation PASS '21 polls over >=600 seconds and zero release-blocking log categories' 'same healthy container, multiple cache polls, all clean-log counts zero' "$ATTEMPT/candidate-log-summary.json"

docker exec -i litellm python - >"$ATTEMPT/topology-final.json" <<'PY'
import hashlib
import json
import os
import urllib.request

def get(path):
    request = urllib.request.Request("http://127.0.0.1:4000" + path, headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]})
    return json.loads(urllib.request.urlopen(request, timeout=30).read())

models = get("/model/info")["data"]
settings = get("/router/settings")["current_values"]
projection = sorted((row["model_name"], row.get("model_info", {}).get("id", "")) for row in models)
fallbacks = settings.get("fallbacks") or []
names = [name for name, _ in projection]
print(json.dumps({
    "rows": len(projection),
    "projection_sha256": hashlib.sha256(json.dumps(projection, separators=(",", ":")).encode()).hexdigest(),
    "fallbacks": len(fallbacks),
    "fallbacks_sha256": hashlib.sha256(json.dumps(fallbacks, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    "default_qualified": sum(name.startswith("chatgpt/") for name in names),
    "account2_qualified": sum(name.startswith("chatgpt-account2/") for name in names),
    "account3": sum("account3" in name for name in names) + sum("account3" in json.dumps(item) for item in fallbacks),
    "cross_profile": settings.get("allow_chatgpt_cross_profile_fallback"),
}, sort_keys=True))
PY
chmod 600 "$ATTEMPT/topology-final.json"
chown root:root "$ATTEMPT/topology-final.json"
cmp -s "$ATTEMPT/topology-baseline.json" "$ATTEMPT/topology-final.json"
sha256sum -c "$ATTEMPT/protected-baseline.sha256" >/dev/null
python3 - "$ENV_FILE" >"$ATTEMPT/non-image-env-final.sha256" <<'PY'
import hashlib
import sys
from pathlib import Path

lines = [line for line in Path(sys.argv[1]).read_text().splitlines() if not line.startswith("LITELLM_IMAGE=")]
print(hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest())
PY
chmod 600 "$ATTEMPT/non-image-env-final.sha256"
chown root:root "$ATTEMPT/non-image-env-final.sha256"
cmp -s "$ATTEMPT/non-image-env-baseline.sha256" "$ATTEMPT/non-image-env-final.sha256"
docker inspect -f '{{.Name}}|{{.Id}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat \
  | sort | atomic_write "$ATTEMPT/dependencies-final.txt"
cmp -s "$ATTEMPT/dependencies-baseline.txt" "$ATTEMPT/dependencies-final.txt"
docker inspect -f '{{range .Mounts}}{{println .Source "|" .Destination "|" .Type "|" .RW}}{{end}}{{range $k,$v := .NetworkSettings.Networks}}{{println $k "|" $v.NetworkID}}{{end}}' litellm \
  | sort | atomic_write "$ATTEMPT/nas-runtime-final.txt"
cmp -s "$ATTEMPT/nas-runtime-baseline.txt" "$ATTEMPT/nas-runtime-final.txt"
grep -Fx '/volume2/docker/litellm/data/op_service_account_token | /run/secrets/op_service_account_token | bind | false' "$ATTEMPT/nas-runtime-final.txt" >/dev/null
python3 - "$STACK/data/op_service_account_token" >"$ATTEMPT/service-account-directory-final.json" <<'PY'
import hashlib
import json
import stat
import sys
from pathlib import Path

path = Path(sys.argv[1])
info = path.lstat()
if path.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o755:
    raise SystemExit("unsafe service-account mount source")
children = sorted(path.iterdir())
if children:
    raise SystemExit("service-account mount source is not empty")
print(json.dumps({"type":"directory","uid":info.st_uid,"gid":info.st_gid,"mode":stat.S_IMODE(info.st_mode),"size":info.st_size,"mtime_ns":info.st_mtime_ns,"ctime_ns":info.st_ctime_ns,"inode":info.st_ino,"device":info.st_dev,"direct_child_projection_sha256":hashlib.sha256(b"[]").hexdigest()},sort_keys=True,separators=(",",":")))
PY
chmod 600 "$ATTEMPT/service-account-directory-final.json"
chown root:root "$ATTEMPT/service-account-directory-final.json"
cmp -s "$ATTEMPT/service-account-directory-baseline.json" "$ATTEMPT/service-account-directory-final.json"
docker ps --format '{{.Names}}|{{.ID}}' | sort | grep -v '^litellm|' | atomic_write "$ATTEMPT/nas-unrelated-final.txt"
grep -v '^litellm|' "$ATTEMPT/nas-containers-baseline.txt" >"$ATTEMPT/nas-unrelated-baseline.txt"
chmod 600 "$ATTEMPT/nas-unrelated-baseline.txt"
chown root:root "$ATTEMPT/nas-unrelated-baseline.txt"
cmp -s "$ATTEMPT/nas-unrelated-baseline.txt" "$ATTEMPT/nas-unrelated-final.txt"

python3 - "$STACK/data" >"$ATTEMPT/credentials-final.tsv" <<'PY'
import hashlib
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
for profile in ("chatgpt-auth", "anthropic-auth"):
    directory = root / profile
    if directory.is_symlink() or directory.resolve() != directory:
        raise SystemExit("unsafe credential root")
    for path in (directory, *sorted(directory.iterdir())):
        info = path.lstat()
        kind = "d" if stat.S_ISDIR(info.st_mode) else "f" if stat.S_ISREG(info.st_mode) else "other"
        label = "ROOT" if path == directory else hashlib.sha256(path.name.encode()).hexdigest()
        category = "root" if path == directory else "lock" if info.st_size == 0 else "credential"
        print("\t".join(map(str, (profile, label, category, kind, info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode), info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino, info.st_dev))))
PY
chmod 600 "$ATTEMPT/credentials-final.tsv"
chown root:root "$ATTEMPT/credentials-final.tsv"
python3 - "$ATTEMPT/credentials-baseline.tsv" "$ATTEMPT/credentials-final.tsv" >"$ATTEMPT/credential-comparison.txt" <<'PY'
import sys
from pathlib import Path

before = {tuple(parts[:2]): parts for parts in (line.split("\t") for line in Path(sys.argv[1]).read_text().splitlines())}
after = {tuple(parts[:2]): parts for parts in (line.split("\t") for line in Path(sys.argv[2]).read_text().splitlines())}
if before.keys() != after.keys():
    raise SystemExit("credential path set changed")
advances = 0
for key, old in before.items():
    new = after[key]
    if old[2] == "lock":
        if old[:9] + old[10:] != new[:9] + new[10:] or int(new[9]) < int(old[9]):
            raise SystemExit("credential lock metadata changed outside allowed ctime advance")
        advances += int(new[9]) > int(old[9])
    elif old != new:
        raise SystemExit("credential metadata changed")
print(f"credential_metadata_gate=PASS lock_ctime_advances={advances}")
PY
chmod 600 "$ATTEMPT/credential-comparison.txt"
chown root:root "$ATTEMPT/credential-comparison.txt"
record preservation PASS 'exact topology, protected hashes, credentials, dependencies, mounts and networks' 'all preservation predicates passed' "$ATTEMPT/credential-comparison.txt"

fedora_projection | atomic_write "$ATTEMPT/fedora-final.txt"
cmp -s "$FEDORA_BASE" "$ATTEMPT/fedora-final.txt"
if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$ATTEMPT/stable-final.tmp" 2>/dev/null; then
  jq -r '.digest // .Digest' "$ATTEMPT/stable-final.tmp" | atomic_write "$ATTEMPT/stable-final.txt"
else
  printf 'MISSING\n' | atomic_write "$ATTEMPT/stable-final.txt"
fi
rm -f "$ATTEMPT/stable-final.tmp"
cmp -s "$STABLE_BASE" "$ATTEMPT/stable-final.txt"
record isolation PASS 'Fedora exact same replacement digest and stable held' 'Fedora unchanged and stable unchanged' "$ATTEMPT/fedora-final.txt"

find "$RELEASE_ROOT" -type d -exec chmod 700 {} +
find "$RELEASE_ROOT" -type f -exec chmod 600 {} +
chown -R root:root "$RELEASE_ROOT"
find "$ATTEMPT" -type f ! -name hash-chain.sha256 -print0 | sort -z | xargs -0 sha256sum | atomic_write "$ATTEMPT/hash-chain.sha256"
sha256sum -c "$ATTEMPT/hash-chain.sha256" >"$ATTEMPT/hash-chain-verification.txt"
chmod 600 "$ATTEMPT/hash-chain-verification.txt"
chown root:root "$ATTEMPT/hash-chain-verification.txt"
test -z "$(find "$RELEASE_ROOT" -type d \( ! -user root -o ! -group root -o ! -perm 700 \) -print -quit)"
test -z "$(find "$RELEASE_ROOT" -type f \( ! -user root -o ! -group root -o ! -perm 600 \) -print -quit)"
record evidence_security PASS 'root:root 0700 directories, 0600 files, verified artifact hashes' 'hierarchy hardened and hash chain reverified' "$ATTEMPT/hash-chain-verification.txt"

jq -n \
  --arg attempt "$ATTEMPT_ID" \
  --arg manifest "$CANDIDATE_MANIFEST" \
  --arg config "$CANDIDATE_CONFIG" \
  --arg container "$CANDIDATE_CONTAINER" \
  --arg started "$CANDIDATE_STARTED" \
  --arg timestamp "$(date -u +%FT%TZ)" \
  '{attempt:$attempt,status:"PASS",decision:"APPROVE_FINAL_CROSS_HOST_QA",manifest:$manifest,config:$config,container:$container,started_at:$started,completed_at:$timestamp,gates:["preflight","deployment_identity","functional","lazymcp","observation","preservation","isolation","evidence_security"]}' \
  | atomic_write "$ATTEMPT/aggregate.json"
chmod 600 "$ATTEMPT/aggregate.json"
chown root:root "$ATTEMPT/aggregate.json"
find "$ATTEMPT" -type f ! -name hash-chain.sha256 ! -name hash-chain-verification.txt -print0 | sort -z | xargs -0 sha256sum | atomic_write "$ATTEMPT/hash-chain.sha256"
sha256sum -c "$ATTEMPT/hash-chain.sha256" >"$ATTEMPT/hash-chain-verification.txt"
chmod 600 "$ATTEMPT/hash-chain-verification.txt"
chown root:root "$ATTEMPT/hash-chain-verification.txt"
test -z "$(find "$RELEASE_ROOT" -type d \( ! -user root -o ! -group root -o ! -perm 700 \) -print -quit)"
test -z "$(find "$RELEASE_ROOT" -type f \( ! -user root -o ! -group root -o ! -perm 600 \) -print -quit)"
ACCEPTED=true
trap - EXIT
printf 'attempt=%s\nstatus=PASS\ndecision=APPROVE_FINAL_CROSS_HOST_QA\nmanifest=%s\nconfig=%s\ncontainer=%s\n' "$ATTEMPT_ID" "$CANDIDATE_MANIFEST" "$CANDIDATE_CONFIG" "$CANDIDATE_CONTAINER"
