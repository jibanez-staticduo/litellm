#!/usr/bin/env bash
set -Eeuo pipefail

readonly STACK=/volume2/docker/litellm
readonly REF=docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly MANIFEST=sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3
readonly CONFIG=sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a
readonly ROOT="$STACK/releases/20260819-clean-telemetry-198-deploy"
readonly ID="reopen3-$(date -u +%Y%m%dT%H%M%SZ)"
readonly ATTEMPT="$ROOT/attempts/$ID"
readonly ROLLBACK="$ROOT/rollback-$ID"

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

install -d -o root -g root -m 700 "$ROOT" "$ROOT/attempts" "$ATTEMPT" "$ROLLBACK"
printf '%s\n' "$ATTEMPT" | atomic_write "$ROOT/reopen3-current-attempt.txt"
cp "$STACK/.env" "$ROLLBACK/.env"
cp "$STACK/docker-compose.yaml" "$ROLLBACK/docker-compose.yaml"
cp "$STACK/start-litellm.sh" "$ROLLBACK/start-litellm.sh"
cp "$STACK/onepassword-mcp-wrapper.sh" "$ROLLBACK/onepassword-mcp-wrapper.sh"
chmod 600 "$ROLLBACK"/* "$ROLLBACK/.env"
chown root:root "$ROLLBACK"/* "$ROLLBACK/.env"

docker inspect -f '{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/container-baseline.txt"
docker ps --format '{{.Names}}|{{.ID}}' | sort | atomic_write "$ATTEMPT/containers-baseline.txt"
docker inspect -f '{{range .Mounts}}{{println .Source "|" .Destination "|" .Type "|" .RW}}{{end}}{{range $k,$v := .NetworkSettings.Networks}}{{println $k "|" $v.NetworkID}}{{end}}' litellm \
  | sort | atomic_write "$ATTEMPT/runtime-baseline.txt"
grep -Fx '/volume2/docker/litellm/data/op_service_account_token | /run/secrets/op_service_account_token | bind | false' "$ATTEMPT/runtime-baseline.txt" >/dev/null
sha256sum "$STACK/docker-compose.yaml" "$STACK/config.yaml" "$STACK/start-litellm.sh" "$STACK/onepassword-mcp-wrapper.sh" \
  | atomic_write "$ATTEMPT/protected-baseline.sha256"
docker inspect -f '{{.Name}}|{{.Id}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat \
  | sort | atomic_write "$ATTEMPT/dependencies-baseline.txt"

python3 - "$STACK/data" >"$ATTEMPT/credentials-baseline.tsv" <<'PY'
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
        expected_mode = 0o700 if category == "root" else 0o600
        if kind != ("d" if category == "root" else "f") or info.st_uid != 0 or info.st_gid != 0 or stat.S_IMODE(info.st_mode) != expected_mode:
            raise SystemExit("unsafe credential metadata")
        print("\t".join(map(str, (profile,label,category,kind,info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode),info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_ino,info.st_dev))))
PY
chmod 600 "$ATTEMPT/credentials-baseline.tsv"
chown root:root "$ATTEMPT/credentials-baseline.tsv"

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
print(json.dumps({"rows":len(projection),"projection_sha256":hashlib.sha256(json.dumps(projection,separators=(",", ":")).encode()).hexdigest(),"fallbacks":len(fallbacks),"fallbacks_sha256":hashlib.sha256(json.dumps(fallbacks,sort_keys=True,separators=(",", ":")).encode()).hexdigest(),"default_qualified":sum(name.startswith("chatgpt/") for name in names),"account2_qualified":sum(name.startswith("chatgpt-account2/") for name in names),"account3":sum("account3" in name for name in names)+sum("account3" in json.dumps(item) for item in fallbacks),"cross_profile":settings.get("allow_chatgpt_cross_profile_fallback")},sort_keys=True))
PY
chmod 600 "$ATTEMPT/topology-baseline.json"
chown root:root "$ATTEMPT/topology-baseline.json"
jq -e '.rows == 32 and .fallbacks == 16 and .default_qualified == 8 and .account2_qualified == 8 and .account3 == 0 and .cross_profile == true' "$ATTEMPT/topology-baseline.json" >/dev/null

docker image inspect -f '{{.Id}}|{{json .RepoDigests}}|{{index .Config.Labels "org.opencontainers.image.version"}}|{{index .Config.Labels "org.opencontainers.image.revision"}}|{{.Architecture}}' "$REF" \
  | atomic_write "$ATTEMPT/candidate-root.txt"
sudo -u staticduo docker image inspect -f '{{.Id}}|{{json .RepoDigests}}|{{index .Config.Labels "org.opencontainers.image.version"}}|{{index .Config.Labels "org.opencontainers.image.revision"}}|{{.Architecture}}' "$REF" \
  | atomic_write "$ATTEMPT/candidate-staticduo.txt"
cmp -s "$ATTEMPT/candidate-root.txt" "$ATTEMPT/candidate-staticduo.txt"
grep -q "$CONFIG" "$ATTEMPT/candidate-root.txt"
grep -q "$MANIFEST" "$ATTEMPT/candidate-root.txt"
grep -q '1.98.0|177c66ef727710a455f058b99f653df9b3e4c0a4|amd64' "$ATTEMPT/candidate-root.txt"

ssh -o BatchMode=yes -o RequestTTY=no -o StrictHostKeyChecking=yes -o ClearAllForwardings=yes -o IdentitiesOnly=yes \
  -o UserKnownHostsFile=/home/staticduo/.ssh/known_hosts -i /home/staticduo/.ssh/id_rsa staticduo@fedora-ssh.staticduo.com \
  'test "$(id -un)" = staticduo; test "$(id -u)" = 1000; docker inspect -f "{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}" litellm' \
  | atomic_write "$ATTEMPT/fedora-baseline.txt"
grep -q "$MANIFEST" "$ATTEMPT/fedora-baseline.txt"
if docker buildx imagetools inspect docker.staticduo.com/litellm:stable --format '{{json .Manifest}}' >"$ATTEMPT/stable.tmp" 2>/dev/null; then
  jq -r '.digest // .Digest' "$ATTEMPT/stable.tmp" | atomic_write "$ATTEMPT/stable-baseline.txt"
else
  printf 'MISSING\n' | atomic_write "$ATTEMPT/stable-baseline.txt"
fi
rm -f "$ATTEMPT/stable.tmp"

python3 - "$STACK/.env" "$REF" <<'PY'
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text().splitlines()
indexes = [index for index, line in enumerate(lines) if line.startswith("LITELLM_IMAGE=")]
if len(indexes) != 1:
    raise SystemExit("invalid image selector")
lines[indexes[0]] = "LITELLM_IMAGE=" + sys.argv[2]
temporary = path.with_name(path.name + ".reopen3")
temporary.write_text("\n".join(lines) + "\n")
os.chmod(temporary, path.stat().st_mode & 0o777)
os.replace(temporary, path)
PY
docker compose --env-file "$STACK/.env" -f "$STACK/docker-compose.yaml" up -d --no-deps litellm >/dev/null
for _ in $(seq 1 90); do
  test "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' litellm)" = healthy && break
  sleep 2
done
docker inspect -f '{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}' litellm \
  | atomic_write "$ATTEMPT/candidate-identity.txt"
grep -q "|$CONFIG|$REF|running|healthy|0|false|" "$ATTEMPT/candidate-identity.txt"
printf 'attempt=%s\nstatus=DEPLOYED_HEALTHY\n' "$ATTEMPT"
