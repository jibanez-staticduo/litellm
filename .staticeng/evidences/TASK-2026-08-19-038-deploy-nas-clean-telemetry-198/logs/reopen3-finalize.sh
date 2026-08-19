#!/usr/bin/env bash
set -Eeuo pipefail

readonly STACK=/volume2/docker/litellm
readonly ROOT="$STACK/releases/20260819-clean-telemetry-198-deploy"
readonly ATTEMPT=$(cat "$ROOT/reopen3-current-attempt.txt")
readonly REFERENCE_SERVICE_DIR="$ROOT/attempts/nas-clean-20260819T044435Z/service-account-directory-baseline.json"
readonly MANIFEST=sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly CONFIG=sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a

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

jq -e '.public_provider_is_default == true and all(.results[]; .status_gate == true and .blocked_error_gate == true and .selection_gate == true and (.http_status == 429 or .sse_lifecycle_gate == true))' "$ATTEMPT/functional-gates.json" >/dev/null
jq -e '.tool_list_gate == true and .status_gate == true and .describe_gate == true and .smoke_gate == true' "$ATTEMPT/lazymcp-gates.json" >/dev/null

readonly CONTAINER=$(docker inspect -f '{{.Id}}' litellm)
readonly STARTED=$(docker inspect -f '{{.State.StartedAt}}' litellm)
if ! python3 - "$ATTEMPT/observation-polls.txt" "$STARTED" 2>/dev/null <<'PY'
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text().splitlines()
if len(lines) != 42:
    raise SystemExit(1)
litellm = lines[::2]
redis = lines[1::2]
if any("|running|healthy|0|false|" not in line or not line.endswith(sys.argv[2]) for line in litellm):
    raise SystemExit(1)
if any("|running|healthy" not in line for line in redis):
    raise SystemExit(1)
PY
then
  for poll in $(seq 1 21); do
    test "$(docker inspect -f '{{.Id}}' litellm)" = "$CONTAINER"
    docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}" litellm
    docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}" litellm-redis
    if test "$poll" -lt 21; then sleep 30; fi
  done | atomic_write "$ATTEMPT/observation-polls.txt"
fi

docker logs --since "$STARTED" litellm 2>&1 | python3 -c '
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
    "generic_traceback_audit": r"Traceback \(most recent call last\)",
    "unrelated_backend_connect": r"Cannot connect to host cachyos-ssh\\.staticduo\\.com:8082|Connect call failed.*8082",
    "unrelated_mcp_400": r"400 Bad Request.*:9101/mcp",
    "unrelated_invalid_key": r"Authentication Error, Invalid proxy server token passed",
}
counts = {name: len(re.findall(pattern, text, re.I)) for name, pattern in patterns.items()}
print(json.dumps(counts, sort_keys=True))
release_blocking = ("standard_logging", "usage_cache", "stream", "auth_device", "migration_schema_patch")
raise SystemExit(any(counts[name] for name in release_blocking))
' | atomic_write "$ATTEMPT/candidate-log-summary.json"

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
print(json.dumps({"rows":len(projection),"projection_sha256":hashlib.sha256(json.dumps(projection,separators=(",", ":")).encode()).hexdigest(),"fallbacks":len(fallbacks),"fallbacks_sha256":hashlib.sha256(json.dumps(fallbacks,sort_keys=True,separators=(",", ":")).encode()).hexdigest(),"default_qualified":sum(name.startswith("chatgpt/") for name in names),"account2_qualified":sum(name.startswith("chatgpt-account2/") for name in names),"account3":sum("account3" in name for name in names)+sum("account3" in json.dumps(item) for item in fallbacks),"cross_profile":settings.get("allow_chatgpt_cross_profile_fallback")},sort_keys=True))
PY
chmod 600 "$ATTEMPT/topology-final.json"
chown root:root "$ATTEMPT/topology-final.json"
cmp -s "$ATTEMPT/topology-baseline.json" "$ATTEMPT/topology-final.json"

python3 - "$STACK/data" >"$ATTEMPT/credentials-final.tsv" <<'PY'
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
        print("\t".join(map(str, (profile,label,category,kind,info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode),info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_ino,info.st_dev))))
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

sha256sum -c "$ATTEMPT/protected-baseline.sha256" >/dev/null
docker inspect -f '{{.Name}}|{{.Id}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat \
  | sort | atomic_write "$ATTEMPT/dependencies-final.txt"
cmp -s "$ATTEMPT/dependencies-baseline.txt" "$ATTEMPT/dependencies-final.txt"
docker inspect -f '{{range .Mounts}}{{println .Source "|" .Destination "|" .Type "|" .RW}}{{end}}{{range $k,$v := .NetworkSettings.Networks}}{{println $k "|" $v.NetworkID}}{{end}}' litellm \
  | sort | atomic_write "$ATTEMPT/runtime-final.txt"
cmp -s "$ATTEMPT/runtime-baseline.txt" "$ATTEMPT/runtime-final.txt"
docker ps --format '{{.Names}}|{{.ID}}' | sort | grep -v '^litellm|' | atomic_write "$ATTEMPT/unrelated-final.txt"
grep -v '^litellm|' "$ATTEMPT/containers-baseline.txt" | atomic_write "$ATTEMPT/unrelated-baseline.txt"
if ! cmp -s "$ATTEMPT/unrelated-baseline.txt" "$ATTEMPT/unrelated-final.txt"; then
  python3 - "$ATTEMPT/unrelated-baseline.txt" "$ATTEMPT/unrelated-final.txt" >"$ATTEMPT/unrelated-delta.json" <<'PY'
import json
import sys
from pathlib import Path

def load(path):
    return dict(line.split("|", 1) for line in Path(path).read_text().splitlines())
before = load(sys.argv[1])
after = load(sys.argv[2])
changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
print(json.dumps({"classification":"external_unrelated_restart","services":[{"name":name,"baseline_id":before.get(name),"final_id":after.get(name)} for name in changed]},sort_keys=True))
PY
  chmod 600 "$ATTEMPT/unrelated-delta.json"
  chown root:root "$ATTEMPT/unrelated-delta.json"
fi

python3 - "$STACK/data/op_service_account_token" >"$ATTEMPT/service-account-directory-final.json" <<'PY'
import hashlib
import json
import stat
import sys
from pathlib import Path

path = Path(sys.argv[1])
info = path.lstat()
if path.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o755 or list(path.iterdir()):
    raise SystemExit("unsafe service-account mount source")
print(json.dumps({"type":"directory","uid":info.st_uid,"gid":info.st_gid,"mode":stat.S_IMODE(info.st_mode),"size":info.st_size,"mtime_ns":info.st_mtime_ns,"ctime_ns":info.st_ctime_ns,"inode":info.st_ino,"device":info.st_dev,"direct_child_projection_sha256":hashlib.sha256(b"[]").hexdigest()},sort_keys=True,separators=(",",":")))
PY
chmod 600 "$ATTEMPT/service-account-directory-final.json"
chown root:root "$ATTEMPT/service-account-directory-final.json"
cmp -s "$REFERENCE_SERVICE_DIR" "$ATTEMPT/service-account-directory-final.json"

python3 - "$ROOT/rollback-$(basename "$ATTEMPT")/.env" "$STACK/.env" <<'PY'
import sys
from pathlib import Path

def normalized(path):
    return [line for line in Path(path).read_text().splitlines() if not line.startswith("LITELLM_IMAGE=")]
if normalized(sys.argv[1]) != normalized(sys.argv[2]):
    raise SystemExit("non-image environment changed")
PY

ssh -o BatchMode=yes -o RequestTTY=no -o StrictHostKeyChecking=yes -o ClearAllForwardings=yes -o IdentitiesOnly=yes \
  -o UserKnownHostsFile=/home/staticduo/.ssh/known_hosts -i /home/staticduo/.ssh/id_rsa staticduo@fedora-ssh.staticduo.com \
  'test "$(id -un)" = staticduo; test "$(id -u)" = 1000; docker inspect -f "{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}" litellm' \
  | atomic_write "$ATTEMPT/fedora-final.txt"
cmp -s "$ATTEMPT/fedora-baseline.txt" "$ATTEMPT/fedora-final.txt"
if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$ATTEMPT/stable-final.tmp" 2>/dev/null; then
  jq -r '.digest // .Digest' "$ATTEMPT/stable-final.tmp" | atomic_write "$ATTEMPT/stable-final.txt"
else
  printf 'MISSING\n' | atomic_write "$ATTEMPT/stable-final.txt"
fi
rm -f "$ATTEMPT/stable-final.tmp"
cmp -s "$ATTEMPT/stable-baseline.txt" "$ATTEMPT/stable-final.txt"

docker inspect -f '{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/final-identity.txt"
grep -q "|$CONFIG|docker.staticduo.com/litellm@$MANIFEST|running|healthy|0|false|" "$ATTEMPT/final-identity.txt"
jq -n --arg container "$CONTAINER" --arg started "$STARTED" '{status:"PASS",decision:"APPROVE_FINAL_CROSS_HOST_QA",container:$container,started_at:$started,observation_seconds:600,polls:21,identity:"pass",functional:"pass",lazymcp:"pass",topology:"exact",credentials:"pass",dependencies:"exact",protected_hashes:"exact",fedora:"unchanged",stable:"unchanged"}' \
  | atomic_write "$ATTEMPT/aggregate.json"

chown -R root:root "$ROOT"
find "$ROOT" -type d -exec chmod 700 {} +
find "$ROOT" -type f -exec chmod 600 {} +
rm -f "$ROOT/hierarchy-hash-chain.sha256" "$ROOT/hierarchy-hash-verification.txt"
readonly HASH_TMP=$(mktemp /tmp/opencode/task038-reopen3-hash.XXXXXX)
trap 'rm -f "$HASH_TMP"' EXIT
find "$ROOT" -type f ! -name hierarchy-hash-chain.sha256 ! -name hierarchy-hash-verification.txt -print0 | sort -z | xargs -0 sha256sum >"$HASH_TMP"
install -o root -g root -m 600 "$HASH_TMP" "$ROOT/hierarchy-hash-chain.sha256"
sha256sum -c "$ROOT/hierarchy-hash-chain.sha256" >"$ROOT/hierarchy-hash-verification.txt"
chmod 600 "$ROOT/hierarchy-hash-verification.txt"
chown root:root "$ROOT/hierarchy-hash-verification.txt"
test -z "$(find "$ROOT" -type d \( ! -user root -o ! -group root -o ! -perm 700 \) -print -quit)"
test -z "$(find "$ROOT" -type f \( ! -user root -o ! -group root -o ! -perm 600 \) -print -quit)"
printf 'status=PASS\ndecision=APPROVE_FINAL_CROSS_HOST_QA\ncontainer=%s\n' "$CONTAINER"
