#!/usr/bin/env bash
set -Eeuo pipefail

readonly STACK=/volume2/docker/litellm
readonly ATTEMPT="$STACK/releases/20260819-clean-telemetry-198-deploy/attempts/nas-clean-20260819T044435Z"
readonly RELEASE_ROOT="$STACK/releases/20260819-clean-telemetry-198-deploy"
readonly FEDORA_HOST=staticduo@fedora-ssh.staticduo.com
readonly FEDORA_KNOWN_HOSTS=/home/staticduo/.ssh/known_hosts
readonly FEDORA_IDENTITY=/home/staticduo/.ssh/id_rsa
readonly ROLLBACK_MANIFEST=sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b
readonly ROLLBACK_CONFIG=sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73

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

jq -n '{gate:"public_default_primary",status:"FAIL",classification:"selection_or_blocked_error",candidate_rolled_back:true,response_content_retained:false}' \
  | atomic_write "$ATTEMPT/functional-failure.json"
rm -f "$ATTEMPT/functional.json"

readonly CONTAINER=$(docker inspect -f '{{.Id}}' litellm)
readonly STARTED=$(docker inspect -f '{{.State.StartedAt}}' litellm)
docker inspect -f '{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/rollback-identity.txt"
grep -q "|$ROLLBACK_CONFIG|docker.staticduo.com/litellm@$ROLLBACK_MANIFEST|running|healthy|0|false|" "$ATTEMPT/rollback-identity.txt"

for poll in $(seq 1 21); do
  test "$(docker inspect -f '{{.Id}}' litellm)" = "$CONTAINER"
  docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}" litellm
  docker inspect -f "${poll}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}" litellm-redis
  if test "$poll" -lt 21; then sleep 30; fi
done | atomic_write "$ATTEMPT/rollback-observation-polls.txt"

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
    "traceback": r"Traceback \(most recent call last\)",
}
counts = {name: len(re.findall(pattern, text, re.I)) for name, pattern in patterns.items()}
print(json.dumps(counts, sort_keys=True))
raise SystemExit(any(counts[name] for name in ("standard_logging", "stream", "auth_device", "migration_schema_patch")))
' | atomic_write "$ATTEMPT/rollback-log-summary.json"

docker exec -i litellm python - >"$ATTEMPT/rollback-topology.json" <<'PY'
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
chmod 600 "$ATTEMPT/rollback-topology.json"
chown root:root "$ATTEMPT/rollback-topology.json"
cmp -s "$ATTEMPT/topology-baseline.json" "$ATTEMPT/rollback-topology.json"

sha256sum -c "$ATTEMPT/protected-baseline.sha256" >/dev/null
python3 - "$STACK/.env" >"$ATTEMPT/rollback-non-image-env.sha256" <<'PY'
import hashlib
import sys
from pathlib import Path

lines = [line for line in Path(sys.argv[1]).read_text().splitlines() if not line.startswith("LITELLM_IMAGE=")]
print(hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest())
PY
chmod 600 "$ATTEMPT/rollback-non-image-env.sha256"
chown root:root "$ATTEMPT/rollback-non-image-env.sha256"
cmp -s "$ATTEMPT/non-image-env-baseline.sha256" "$ATTEMPT/rollback-non-image-env.sha256"

docker inspect -f '{{.Name}}|{{.Id}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat \
  | sort | atomic_write "$ATTEMPT/rollback-dependencies.txt"
cmp -s "$ATTEMPT/dependencies-baseline.txt" "$ATTEMPT/rollback-dependencies.txt"
docker inspect -f '{{range .Mounts}}{{println .Source "|" .Destination "|" .Type "|" .RW}}{{end}}{{range $k,$v := .NetworkSettings.Networks}}{{println $k "|" $v.NetworkID}}{{end}}' litellm \
  | sort | atomic_write "$ATTEMPT/rollback-runtime.txt"
cmp -s "$ATTEMPT/nas-runtime-baseline.txt" "$ATTEMPT/rollback-runtime.txt"

python3 - "$STACK/data" >"$ATTEMPT/rollback-credentials.tsv" <<'PY'
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
chmod 600 "$ATTEMPT/rollback-credentials.tsv"
chown root:root "$ATTEMPT/rollback-credentials.tsv"
python3 - "$ATTEMPT/credentials-baseline.tsv" "$ATTEMPT/rollback-credentials.tsv" >"$ATTEMPT/rollback-credential-comparison.txt" <<'PY'
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
chmod 600 "$ATTEMPT/rollback-credential-comparison.txt"
chown root:root "$ATTEMPT/rollback-credential-comparison.txt"

fedora_projection | atomic_write "$ATTEMPT/fedora-rollback-final.txt"
cmp -s "$ATTEMPT/fedora-baseline.txt" "$ATTEMPT/fedora-rollback-final.txt"
if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$ATTEMPT/stable-rollback.tmp" 2>/dev/null; then
  jq -r '.digest // .Digest' "$ATTEMPT/stable-rollback.tmp" | atomic_write "$ATTEMPT/stable-rollback-final.txt"
else
  printf 'MISSING\n' | atomic_write "$ATTEMPT/stable-rollback-final.txt"
fi
rm -f "$ATTEMPT/stable-rollback.tmp"
cmp -s "$ATTEMPT/stable-baseline.txt" "$ATTEMPT/stable-rollback-final.txt"

jq -n --arg container "$CONTAINER" --arg started "$STARTED" '{status:"PASS",decision:"ROLLBACK_HEALTHY_RELEASE_REJECTED",container:$container,started_at:$started,observation_seconds:600,polls:21,topology:"exact",credentials:"pass",dependencies:"exact",protected_hashes:"exact",fedora:"unchanged",stable:"unchanged"}' \
  | atomic_write "$ATTEMPT/rollback-aggregate.json"

chown -R root:root "$RELEASE_ROOT"
find "$RELEASE_ROOT" -type d -exec chmod 700 {} +
find "$RELEASE_ROOT" -type f -exec chmod 600 {} +
rm -f "$RELEASE_ROOT/hierarchy-hash-chain.sha256" "$RELEASE_ROOT/hierarchy-hash-verification.txt"
readonly HASH_TMP=$(mktemp /tmp/opencode/task038-rollback-hash.XXXXXX)
trap 'rm -f "$HASH_TMP"' EXIT
find "$RELEASE_ROOT" -type f ! -name hierarchy-hash-chain.sha256 ! -name hierarchy-hash-verification.txt -print0 | sort -z | xargs -0 sha256sum >"$HASH_TMP"
install -o root -g root -m 600 "$HASH_TMP" "$RELEASE_ROOT/hierarchy-hash-chain.sha256"
sha256sum -c "$RELEASE_ROOT/hierarchy-hash-chain.sha256" >"$RELEASE_ROOT/hierarchy-hash-verification.txt"
chmod 600 "$RELEASE_ROOT/hierarchy-hash-verification.txt"
chown root:root "$RELEASE_ROOT/hierarchy-hash-verification.txt"
test -z "$(find "$RELEASE_ROOT" -type d \( ! -user root -o ! -group root -o ! -perm 700 \) -print -quit)"
test -z "$(find "$RELEASE_ROOT" -type f \( ! -user root -o ! -group root -o ! -perm 600 \) -print -quit)"
printf 'rollback_verification=PASS\ndecision=RELEASE_REJECTED\n'
