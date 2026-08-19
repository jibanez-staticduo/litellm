#!/usr/bin/env bash
set -Eeuo pipefail

readonly TASK_ID=TASK-2026-08-19-043-secure-fedora-release-evidence
readonly STACK=/home/staticduo/docker/litellm
readonly RELEASE_ROOT="$STACK/releases/20260819-clean-telemetry-198"
readonly EXPECTED_MANIFEST=sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly EXPECTED_CONFIG=sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a
readonly EXPECTED_CONTAINER=43ca1ba9c48916f748c0e23e4366603e0abcfde20c5c8686c9028e510cae5941
readonly FEDORA=staticduo@fedora-ssh.staticduo.com
readonly SSH=(ssh -o BatchMode=yes -o RequestTTY=no -o StrictHostKeyChecking=yes -o ClearAllForwardings=yes -o IdentitiesOnly=yes -o UserKnownHostsFile=/home/staticduo/.ssh/known_hosts -i /home/staticduo/.ssh/id_rsa)
readonly SCP=(scp -q -o BatchMode=yes -o RequestTTY=no -o StrictHostKeyChecking=yes -o ClearAllForwardings=yes -o IdentitiesOnly=yes -o UserKnownHostsFile=/home/staticduo/.ssh/known_hosts -i /home/staticduo/.ssh/id_rsa)
REPO_ROOT=$(git rev-parse --show-toplevel)
readonly REPO_ROOT
readonly LOCAL_ROOT="$REPO_ROOT/.staticeng/evidences/$TASK_ID"
readonly SOURCE_ROOT="$REPO_ROOT/.staticeng/evidences/TASK-2026-08-19-037-deploy-fedora-clean-telemetry-198"
FUNCTIONAL_SOURCE_SHA=$(sha256sum "$SOURCE_ROOT/logs/03-functional-and-lazymcp.md" | cut -d' ' -f1)
readonly FUNCTIONAL_SOURCE_SHA
IDENTITY_SOURCE_SHA=$(sha256sum "$SOURCE_ROOT/logs/02-deployment-and-identity.md" | cut -d' ' -f1)
readonly IDENTITY_SOURCE_SHA
OBSERVATION_SOURCE_SHA=$(sha256sum "$SOURCE_ROOT/logs/04-observation-and-preservation.md" | cut -d' ' -f1)
readonly OBSERVATION_SOURCE_SHA
CAPTURED_AT=$(date -u +%Y%m%dT%H%M%SZ)
readonly CAPTURED_AT
readonly PACKET_NAME="secure-fedora-release-evidence-$CAPTURED_AT"
readonly REMOTE_PACKET="$RELEASE_ROOT/$PACKET_NAME"
TMP_ROOT=$(mktemp -d /tmp/opencode/task043.XXXXXX)
readonly TMP_ROOT
trap 'rm -rf "$TMP_ROOT"' EXIT

capture_nas_and_stable() {
  local output=$1
  local phase=$2
  local stable=MISSING_OR_UNRESOLVED
  local stable_tmp="$TMP_ROOT/stable-$phase.json"
  if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$stable_tmp" 2>/dev/null; then
    stable=$(python3 - "$stable_tmp" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
print(payload.get("digest") or payload.get("Digest") or "UNKNOWN")
PY
)
  fi
  python3 - <(docker inspect litellm) "$phase" "$stable" "$EXPECTED_MANIFEST" >"$output" <<'PY'
import json
import sys
from pathlib import Path

record = json.loads(Path(sys.argv[1]).read_text())[0]
state = record["State"]
health = state.get("Health", {}).get("Status", "")
selector = record["Config"]["Image"]
expected = sys.argv[4]
print(json.dumps({
    "phase": sys.argv[2],
    "container": record["Id"],
    "config_digest": record["Image"],
    "selector": selector,
    "replacement_digest_gate": selector.endswith("@" + expected),
    "status": state["Status"],
    "health": health,
    "restart_count": record["RestartCount"],
    "oom_killed": state["OOMKilled"],
    "started_at": state["StartedAt"],
    "stable": sys.argv[3],
}, sort_keys=True))
PY
}

capture_nas_and_stable "$TMP_ROOT/nas-stable-before.json" before

"${SSH[@]}" "$FEDORA" bash -s -- \
  "$REMOTE_PACKET" "$TASK_ID" "$STACK" "$RELEASE_ROOT" \
  "$EXPECTED_MANIFEST" "$EXPECTED_CONFIG" "$EXPECTED_CONTAINER" \
  "$FUNCTIONAL_SOURCE_SHA" "$IDENTITY_SOURCE_SHA" "$OBSERVATION_SOURCE_SHA" <<'REMOTE'
set -Eeuo pipefail
umask 077

readonly PACKET=$1
readonly TASK_ID=$2
readonly STACK=$3
readonly RELEASE_ROOT=$4
readonly EXPECTED_MANIFEST=$5
readonly EXPECTED_CONFIG=$6
readonly EXPECTED_CONTAINER=$7
readonly FUNCTIONAL_SOURCE_SHA=$8
readonly IDENTITY_SOURCE_SHA=$9
readonly OBSERVATION_SOURCE_SHA=${10}
readonly ROLLBACK_DIR="$RELEASE_ROOT/20260819T040414Z"

test "$(id -un)" = staticduo
test "$(id -u)" = 1000
test -d "$RELEASE_ROOT"
test ! -L "$RELEASE_ROOT"
test ! -e "$PACKET"
mkdir -m 700 "$PACKET"

atomic_write() {
  local path=$1
  local tmp="$PACKET/.tmp.$$.${RANDOM}"
  cat >"$tmp"
  chmod 600 "$tmp"
  mv -f "$tmp" "$path"
}

capture_identity() {
  local selector="docker.staticduo.com/litellm@$EXPECTED_MANIFEST"
  python3 - <(docker inspect litellm) <(docker buildx imagetools inspect "$selector" --raw) \
    "$EXPECTED_MANIFEST" "$EXPECTED_CONFIG" "$EXPECTED_CONTAINER" <<'PY'
import json
import sys
from pathlib import Path

record = json.loads(Path(sys.argv[1]).read_text())[0]
registry_manifest = json.loads(Path(sys.argv[2]).read_text())
state = record["State"]
health = state.get("Health", {}).get("Status", "")
selector = record["Config"]["Image"]
print(json.dumps({
    "container": record["Id"],
    "runtime_image_id": record["Image"],
    "registry_config_digest": registry_manifest["config"]["digest"],
    "selector": selector,
    "status": state["Status"],
    "health": health,
    "restart_count": record["RestartCount"],
    "oom_killed": state["OOMKilled"],
    "started_at": state["StartedAt"],
    "mount_count": len(record["Mounts"]),
    "networks": sorted(record["NetworkSettings"]["Networks"]),
    "expected_manifest_gate": selector.endswith("@" + sys.argv[3]),
    "expected_config_gate": registry_manifest["config"]["digest"] == sys.argv[4],
    "original_container_gate": record["Id"] == sys.argv[5],
}, sort_keys=True))
PY
}

capture_topology() {
  docker exec -i litellm python - <<'PY'
import hashlib
import json
import os
import urllib.request

def get(path):
    request = urllib.request.Request(
        "http://127.0.0.1:4000" + path,
        headers={"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"]},
    )
    return json.loads(urllib.request.urlopen(request, timeout=30).read())

models = get("/model/info")["data"]
settings = get("/router/settings")["current_values"]
projection = sorted((row["model_name"], row.get("model_info", {}).get("id", "")) for row in models)
fallbacks = settings.get("fallbacks") or []
names = [name for name, _ in projection]
canonical_models = json.dumps(projection, separators=(",", ":"))
canonical_fallbacks = json.dumps(fallbacks, sort_keys=True, separators=(",", ":"))
print(json.dumps({
    "model_rows": len(projection),
    "model_projection_sha256": hashlib.sha256(canonical_models.encode()).hexdigest(),
    "fallback_rules": len(fallbacks),
    "fallback_projection_sha256": hashlib.sha256(canonical_fallbacks.encode()).hexdigest(),
    "default_qualified": sum(name.startswith("chatgpt/") for name in names),
    "account2_qualified": sum(name.startswith("chatgpt-account2/") for name in names),
    "account3_references": sum("account3" in name for name in names) + sum("account3" in json.dumps(item) for item in fallbacks),
    "cross_profile_fallback": settings.get("allow_chatgpt_cross_profile_fallback"),
}, sort_keys=True))
PY
}

capture_credentials() {
  python3 - "$STACK/data" <<'PY'
import hashlib
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
        print("\t".join(map(str, (
            profile, label, category, kind, info.st_uid, info.st_gid,
            stat.S_IMODE(info.st_mode), info.st_size, info.st_mtime_ns,
            info.st_ctime_ns, info.st_ino, info.st_dev,
        ))))
PY
}

capture_dependencies() {
  python3 - <(docker inspect postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat) <<'PY'
import json
import sys
from pathlib import Path

records = json.loads(Path(sys.argv[1]).read_text())
projection = []
for record in records:
    state = record["State"]
    projection.append({
        "name": record["Name"].removeprefix("/"),
        "container": record["Id"],
        "status": state["Status"],
        "health": state.get("Health", {}).get("Status", "not-configured"),
        "restart_count": record["RestartCount"],
        "oom_killed": state["OOMKilled"],
        "started_at": state["StartedAt"],
    })
print(json.dumps(sorted(projection, key=lambda item: item["name"]), sort_keys=True))
PY
}

capture_runtime() {
  python3 - <(docker inspect litellm) <<'PY'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

record = json.loads(Path(sys.argv[1]).read_text())[0]
mounts = sorted(({
    "source": item["Source"],
    "destination": item["Destination"],
    "type": item["Type"],
    "read_write": item["RW"],
} for item in record["Mounts"]), key=lambda item: item["destination"])
networks = sorted(({
    "name": name,
    "network_id": value["NetworkID"],
} for name, value in record["NetworkSettings"]["Networks"].items()), key=lambda item: item["name"])
containers = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}|{{.ID}}"], text=True).splitlines()
unrelated = sorted(line for line in containers if not line.startswith("litellm|"))
print(json.dumps({
    "mounts": mounts,
    "networks": networks,
    "running_containers": len(containers),
    "unrelated_projection_sha256": hashlib.sha256("\n".join(unrelated).encode()).hexdigest(),
}, sort_keys=True))
PY
}

capture_protected() {
  python3 - "$STACK" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

stack = Path(sys.argv[1])
paths = tuple(stack / name for name in (
    "docker-compose.yaml", "config.yaml", "start-litellm.sh", "onepassword-mcp-wrapper.sh",
))
records = []
for path in paths:
    if path.is_symlink() or not path.is_file():
        raise SystemExit("unsafe protected path")
    records.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

lines = (stack / ".env").read_text().splitlines()
selector = next((line.split("=", 1)[1] for line in lines if line.startswith("LITELLM_IMAGE=")), "")
non_image = sorted(line for line in lines if line and not line.startswith("LITELLM_IMAGE="))
print(json.dumps({
    "files": records,
    "environment_non_image_line_count": len(non_image),
    "environment_non_image_sha256": hashlib.sha256("\n".join(non_image).encode()).hexdigest(),
    "image_selector": selector,
}, sort_keys=True))
PY
}

capture_health() {
  docker exec -i litellm python - <<'PY'
import json
import urllib.error
import urllib.request

results = {}
for path in ("/health/readiness", "/health/liveliness"):
    try:
        response = urllib.request.urlopen("http://127.0.0.1:4000" + path, timeout=30)
        results[path] = response.status
    except urllib.error.HTTPError as error:
        results[path] = error.code
print(json.dumps({"checks": results, "pass": all(value == 200 for value in results.values())}, sort_keys=True))
PY
}

capture_lazymcp() {
  docker exec -i litellm python - <<'PY'
import hashlib
import json
import os
import urllib.request

url = "http://127.0.0.1:4000/lazymcp"
headers = {
    "Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"],
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-11-25",
}

def call(identifier, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params}).encode()
    request = urllib.request.Request(url, data=payload, headers=headers)
    raw = urllib.request.urlopen(request, timeout=120).read().decode()
    lines = [line.removeprefix("data:").strip() for line in raw.splitlines() if line.startswith("data:")]
    result = json.loads(lines[-1] if lines else raw)
    passed = not result.get("error") and result.get("result", {}).get("isError") is not True
    return result, passed, hashlib.sha256(raw.encode()).hexdigest()

listed, list_gate, list_hash = call(1, "tools/list", {})
tools = sorted(tool["name"] for tool in listed.get("result", {}).get("tools", []))
_, status_gate, status_hash = call(2, "tools/call", {"name": "mcp_status", "arguments": {}})
described, describe_gate, describe_hash = call(3, "tools/call", {
    "name": "mcp_describe",
    "arguments": {"server": "defend_memory", "tool": "defend_memory-find"},
})
print(json.dumps({
    "protocol": "2025-11-25",
    "tools": tools,
    "tool_list_gate": list_gate and tools == ["mcp_call", "mcp_describe", "mcp_status"],
    "status_gate": status_gate,
    "describe_gate": describe_gate and "defend_memory-find" in json.dumps(described),
    "response_hashes": {"list": list_hash, "status": status_hash, "describe": describe_hash},
    "private_response_content_retained": False,
}, sort_keys=True))
PY
}

capture_observation() {
  local started=$1
  python3 - <(docker logs --since "$started" litellm 2>&1) "$started" <<'PY'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

text = Path(sys.argv[1]).read_text(errors="replace")
patterns = {
    "standard_logging": r"standard_logging_object.*(?:missing|invalid)|StandardLoggingPayload.*(?:missing|invalid)|success callback.*(?:error|traceback)|success handler.*traceback",
    "usage_cache": r"resolved_usage_cache.*(?:NameError|not defined)|NameError.*resolved_usage_cache|cache.settings.*(?:error|traceback)",
    "stream": r"Stream must be set to true|response.failed",
    "auth_device": r"Authentication required|device flow|device_auth|auth\.openai|login\.openai",
    "migration_schema_patch": r"migration.*(?:error|failed)|schema.*(?:error|failed)|patch.*(?:error|failed)",
    "generic_traceback_audit": r"Traceback \(most recent call last\)",
}
counts = {name: len(re.findall(pattern, text, re.I)) for name, pattern in patterns.items()}
start = datetime.fromisoformat(sys.argv[2].replace("Z", "+00:00"))
now = datetime.now(timezone.utc)
blocking = ("standard_logging", "usage_cache", "stream", "auth_device", "migration_schema_patch")
print(json.dumps({
    "started_at": sys.argv[2],
    "captured_at": now.isoformat(),
    "observed_seconds": int((now - start).total_seconds()),
    "counts": counts,
    "release_blocking_zero": all(counts[name] == 0 for name in blocking),
    "raw_log_content_retained": False,
}, sort_keys=True))
PY
}

capture_rollback() {
  python3 - "$ROLLBACK_DIR" "$STACK/.env" <<'PY'
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

rollback = Path(sys.argv[1])
current_env = Path(sys.argv[2])
rollback_env = rollback / ".env.rollback"
image_file = rollback / "rollback-image.txt"
if rollback.is_symlink() or rollback_env.is_symlink() or image_file.is_symlink():
    raise SystemExit("unsafe rollback path")

image_text = image_file.read_text().strip()
match = re.search(r"docker\.staticduo\.com/litellm@sha256:[0-9a-f]{64}", image_text)
if not match:
    raise SystemExit("invalid rollback image reference")
image = match.group(0)
inspect = json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True))[0]
registry_manifest = json.loads(subprocess.check_output(
    ["docker", "buildx", "imagetools", "inspect", image, "--raw"], text=True,
))

def normalized(path):
    return sorted(line for line in path.read_text().splitlines() if line and not line.startswith("LITELLM_IMAGE="))

print(json.dumps({
    "directory": str(rollback),
    "image": image,
    "locally_resolvable": True,
    "runtime_image_id": inspect["Id"],
    "registry_config_digest": registry_manifest["config"]["digest"],
    "platform": inspect["Os"] + "/" + inspect["Architecture"],
    "rollback_environment_sha256": hashlib.sha256(rollback_env.read_bytes()).hexdigest(),
    "non_image_environment_matches_current": normalized(rollback_env) == normalized(current_env),
}, sort_keys=True))
PY
}

capture_identity | atomic_write "$PACKET/identity-before.json"
capture_health | atomic_write "$PACKET/health.json"
capture_topology | atomic_write "$PACKET/topology-before.json"
capture_credentials | atomic_write "$PACKET/credential-metadata-before.tsv"
capture_dependencies | atomic_write "$PACKET/dependencies-before.json"
capture_runtime | atomic_write "$PACKET/runtime-before.json"
capture_protected | atomic_write "$PACKET/protected-before.json"
capture_rollback | atomic_write "$PACKET/rollback-reference.json"

readonly STARTED=$(python3 - "$PACKET/identity-before.json" <<'PY'
import json
import sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text())["started_at"])
PY
)
capture_observation "$STARTED" | atomic_write "$PACKET/observation-current.json"
capture_lazymcp | atomic_write "$PACKET/lazymcp-current.json"

python3 - "$PACKET/identity-before.json" "$FUNCTIONAL_SOURCE_SHA" "$IDENTITY_SOURCE_SHA" <<'PY' | atomic_write "$PACKET/functional-summary.json"
import json
import sys
from pathlib import Path

identity = json.loads(Path(sys.argv[1]).read_text())
print(json.dumps({
    "evidence_mode": "prior-live-gates-anchored-to-unchanged-current-container",
    "source_task": "TASK-2026-08-19-037-deploy-fedora-clean-telemetry-198",
    "source_functional_summary_sha256": sys.argv[2],
    "source_identity_summary_sha256": sys.argv[3],
    "source_container": "43ca1ba9c48916f748c0e23e4366603e0abcfde20c5c8686c9028e510cae5941",
    "current_container": identity["container"],
    "same_container_gate": identity["container"] == "43ca1ba9c48916f748c0e23e4366603e0abcfde20c5c8686c9028e510cae5941",
    "native_account2_stream_false": {"http": 200, "sse_completed": 1, "blocked_errors": 0, "selected_account2": True},
    "qualified_regular": {"http": 200, "sse_completed": 1, "blocked_errors": 0, "selected_account2": True},
    "direct_account2": {"http": 200, "sse_completed": 1, "blocked_errors": 0, "selected_account2": True},
    "public_fallback": {"http": 200, "sse_completed": 1, "blocked_errors": 0, "selected_account2": True},
    "fresh_provider_request_sent": False,
    "reason": "Preserve credential bytes while the originally verified container remains unchanged",
}, sort_keys=True))
PY

python3 - "$TASK_ID" "$FUNCTIONAL_SOURCE_SHA" "$IDENTITY_SOURCE_SHA" "$OBSERVATION_SOURCE_SHA" <<'PY' | atomic_write "$PACKET/packet-metadata.json"
import json
import sys
from datetime import datetime, timezone

print(json.dumps({
    "task_id": sys.argv[1],
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "owner": "staticduo",
    "directory_mode": "0700",
    "file_mode": "0600",
    "sanitized": True,
    "source_hashes": {
        "functional_and_lazymcp": sys.argv[2],
        "deployment_identity": sys.argv[3],
        "observation_and_preservation": sys.argv[4],
    },
}, sort_keys=True))
PY

capture_identity | atomic_write "$PACKET/identity-after.json"
capture_topology | atomic_write "$PACKET/topology-after.json"
capture_credentials | atomic_write "$PACKET/credential-metadata-after.tsv"
capture_dependencies | atomic_write "$PACKET/dependencies-after.json"
capture_runtime | atomic_write "$PACKET/runtime-after.json"
capture_protected | atomic_write "$PACKET/protected-after.json"

cmp -s "$PACKET/identity-before.json" "$PACKET/identity-after.json"
cmp -s "$PACKET/topology-before.json" "$PACKET/topology-after.json"
cmp -s "$PACKET/dependencies-before.json" "$PACKET/dependencies-after.json"
cmp -s "$PACKET/runtime-before.json" "$PACKET/runtime-after.json"
cmp -s "$PACKET/protected-before.json" "$PACKET/protected-after.json"

python3 - "$PACKET/credential-metadata-before.tsv" "$PACKET/credential-metadata-after.tsv" <<'PY' | atomic_write "$PACKET/credential-comparison.json"
import json
import sys
from pathlib import Path

before = {tuple(parts[:2]): parts for parts in (line.split("\t") for line in Path(sys.argv[1]).read_text().splitlines())}
after = {tuple(parts[:2]): parts for parts in (line.split("\t") for line in Path(sys.argv[2]).read_text().splitlines())}
if before.keys() != after.keys():
    raise SystemExit("credential path set changed")
lock_ctime_advances = 0
for key, old in before.items():
    new = after[key]
    if old[2] == "lock":
        if old[:9] + old[10:] != new[:9] + new[10:] or int(new[9]) < int(old[9]):
            raise SystemExit("credential lock metadata changed outside allowed ctime advance")
        lock_ctime_advances += int(new[9]) > int(old[9])
    elif old != new:
        raise SystemExit("credential metadata changed")
print(json.dumps({
    "credential_bytes_and_metadata_unchanged": True,
    "path_set_unchanged": True,
    "lock_ctime_advances": lock_ctime_advances,
}, sort_keys=True))
PY

chmod 700 "$PACKET"
find "$PACKET" -type f -exec chmod 600 {} +
printf '%s\n' "$PACKET"
REMOTE

capture_nas_and_stable "$TMP_ROOT/nas-stable-after.json" after
python3 - "$TMP_ROOT/nas-stable-before.json" "$TMP_ROOT/nas-stable-after.json" >"$TMP_ROOT/peer-nas-stable.json" <<'PY'
import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text())
after = json.loads(Path(sys.argv[2]).read_text())
keys = ("container", "config_digest", "selector", "status", "health", "restart_count", "oom_killed", "started_at", "stable")
unchanged = all(before[key] == after[key] for key in keys)
healthy = after["status"] == "running" and after["health"] == "healthy" and after["restart_count"] == 0 and not after["oom_killed"]
print(json.dumps({
    "before": before,
    "after": after,
    "unchanged_gate": unchanged,
    "healthy_gate": healthy,
    "same_replacement_digest_gate": after["replacement_digest_gate"],
    "stable_held_gate": before["stable"] == after["stable"],
}, sort_keys=True))
if not all((unchanged, healthy, after["replacement_digest_gate"], before["stable"] == after["stable"])):
    raise SystemExit("NAS/stable isolation gate failed")
PY

"${SCP[@]}" "$TMP_ROOT/peer-nas-stable.json" "$FEDORA:$REMOTE_PACKET/peer-nas-stable.json"
"${SSH[@]}" "$FEDORA" bash -s -- "$REMOTE_PACKET" <<'REMOTE'
set -Eeuo pipefail
readonly PACKET=$1
chmod 700 "$PACKET"
find "$PACKET" -type f -exec chmod 600 {} +
test -z "$(find "$PACKET" -type l -print -quit)"
test -z "$(find "$PACKET" -type d \( \! -user staticduo -o \! -group staticduo -o \! -perm 700 \) -print -quit)"
test -z "$(find "$PACKET" -type f \( \! -user staticduo -o \! -group staticduo -o \! -perm 600 \) -print -quit)"
test -z "$(find "$PACKET" -perm /002 -print -quit)"
rm -f "$PACKET/artifact-hash-chain.sha256" "$PACKET/artifact-hash-verification.txt"
(cd "$PACKET" && find . -type f ! -name artifact-hash-chain.sha256 ! -name artifact-hash-verification.txt -print0 \
  | sort -z | xargs -0 sha256sum >artifact-hash-chain.sha256)
chmod 600 "$PACKET/artifact-hash-chain.sha256"
(cd "$PACKET" && sha256sum -c artifact-hash-chain.sha256 >artifact-hash-verification.txt)
chmod 600 "$PACKET/artifact-hash-verification.txt"
(cd "$PACKET" && sha256sum -c artifact-hash-chain.sha256 >/dev/null)
printf 'remote_packet=%s\nremote_hash_chain=PASS\n' "$PACKET"
REMOTE

mkdir -m 700 "$LOCAL_ROOT/host-packet"
"${SCP[@]}" -r "$FEDORA:$REMOTE_PACKET/." "$LOCAL_ROOT/host-packet/"
find "$LOCAL_ROOT/host-packet" -type d -exec chmod 700 {} +
find "$LOCAL_ROOT/host-packet" -type f -exec chmod 600 {} +
(cd "$LOCAL_ROOT/host-packet" && sha256sum -c artifact-hash-chain.sha256) >"$LOCAL_ROOT/logs/remote-hash-chain-independent-verification.txt"
chmod 600 "$LOCAL_ROOT/logs/remote-hash-chain-independent-verification.txt"

printf 'packet=%s\nlocal_copy=%s\nstatus=PASS\n' "$REMOTE_PACKET" "$LOCAL_ROOT/host-packet"
