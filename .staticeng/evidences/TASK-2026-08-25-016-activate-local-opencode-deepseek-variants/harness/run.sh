#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT="$ROOT/logs/strict-loopback"

rm -rf "$OUTPUT"
mkdir -p "$OUTPUT"
sha256sum /home/staticduo/.opencode/bin/opencode /home/staticduo/git/opencode-litellm/dist/index.js \
  >"$OUTPUT/artifact-checksums.log"

unshare --net --map-root-user sh -eu <<EOF
export HOME=/tmp/opencode-deepseek-strict-home
export XDG_CONFIG_HOME=/tmp/opencode-deepseek-strict-config
export XDG_DATA_HOME=/home/staticduo/.local/share
export XDG_CACHE_HOME=/home/staticduo/.cache
export XDG_STATE_HOME=/tmp/opencode-deepseek-strict-state
export OPENCODE_CONFIG_DIR=\$XDG_CONFIG_HOME/opencode
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export OPENCODE_DISABLE_MODELS_FETCH=1
export OPENCODE_DISABLE_AUTOUPDATE=1
export OPENCODE_DISABLE_SHARE=1
export OPENCODE_DISABLE_LSP_DOWNLOAD=1
export OPENCODE_DISABLE_DEFAULT_PLUGINS=1
export OPENCODE_FAKE_VCS=git
export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost

rm -rf "\$HOME" "\$XDG_CONFIG_HOME" "\$XDG_STATE_HOME"
mkdir -p "\$HOME" "\$OPENCODE_CONFIG_DIR" "\$XDG_STATE_HOME"
python3 - <<'PY'
import fcntl
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
request = struct.pack("16sh", b"lo", 0)
flags = struct.unpack("16sh", fcntl.ioctl(sock, 0x8913, request))[1]
fcntl.ioctl(sock, 0x8914, struct.pack("16sh", b"lo", flags | 0x1 | 0x40))
PY
cat > "\$OPENCODE_CONFIG_DIR/opencode.json" <<'JSON'
{
  "\$schema": "https://opencode.ai/config.json",
  "plugin": [[
    "file:///home/staticduo/git/opencode-litellm/dist/index.js",
    {
      "baseURL": "http://127.0.0.1:18765/v1",
      "apiKey": "fixture-token-not-real",
      "providerKey": "LiteLLM",
      "providerName": "LiteLLM",
      "providerOverrides": {"npm": "@ai-sdk/openai-compatible"}
    }
  ]],
  "model": "LiteLLM/deepseek-v4-flash-fp8-mtp",
  "small_model": "LiteLLM/deepseek-v4-flash-fp8-mtp",
  "permission": {"*": "allow"}
}
JSON

{
  echo "isolation=unshare --net --map-root-user"
  echo "opencode_version=\$(opencode --version)"
  echo "interfaces_begin"
  cat /proc/net/dev
  echo "interfaces_end"
  echo "routes_begin"
  cat /proc/net/route
  echo "routes_end"
  node - <<'JS'
const net = require("node:net")
const socket = net.connect({host: "1.1.1.1", port: 443})
socket.setTimeout(2000)
socket.on("connect", () => { console.log("external_connect=UNEXPECTED_SUCCESS"); process.exit(7) })
socket.on("error", (error) => { console.log("external_connect=blocked code=" + error.code); process.exit(0) })
socket.on("timeout", () => { console.log("external_connect=blocked timeout"); socket.destroy(); process.exit(0) })
JS
} > "$OUTPUT/network-isolation.log"

python3 "$ROOT/harness/mock_server.py" "$OUTPUT/sanitized-loopback-bodies.jsonl" >"$OUTPUT/mock-server.log" 2>&1 &
server_pid=\$!
trap 'kill "\$server_pid" 2>/dev/null || true' EXIT

attempt=0
until curl --silent --fail http://127.0.0.1:18765/model_group/info >/dev/null; do
  attempt=\$((attempt + 1))
  [ "\$attempt" -lt 50 ] || exit 1
  sleep 0.1
done

opencode debug config >"$OUTPUT/resolved-config.json"
opencode serve --hostname 127.0.0.1 --port 18766 >"$OUTPUT/opencode-server.log" 2>&1 &
opencode_pid=\$!
trap 'kill "\$opencode_pid" "\$server_pid" 2>/dev/null || true' EXIT
attempt=0
until curl --silent --fail http://127.0.0.1:18766/global/health >/dev/null; do
  attempt=\$((attempt + 1))
  [ "\$attempt" -lt 100 ] || exit 1
  sleep 0.1
done
OUTPUT="$OUTPUT" node --input-type=module <<'JS'
import { createOpencodeClient } from "/home/staticduo/.cache/opencode/node_modules/@opencode-ai/sdk/dist/v2/client.js"
import { readFile, writeFile } from "node:fs/promises"

const client = createOpencodeClient({ baseUrl: "http://127.0.0.1:18766", directory: "/tmp" })
const cases = []
for (const alias of ["deepseek-v4-flash-fp8-mtp", "deepseek-v4-flash-fp8-mtp-norefusal"]) {
  for (const effort of ["off", "low", "high", "max"]) {
    const created = await client.session.create({ directory: "/tmp", title: "strict-loopback" })
    if (created.error) throw new Error(JSON.stringify(created.error))
    cases.push({alias, effort, sessionID: created.data.id})
  }
}
for (const {alias, effort, sessionID} of cases) {
  client.session.prompt({
    sessionID,
    directory: "/tmp",
    model: { providerID: "LiteLLM", modelID: alias },
    variant: effort,
    parts: [{ type: "text", text: "fixture prompt for strict loopback capture" }],
  }).catch(() => {})
}
const capturePath = process.env.OUTPUT + "/sanitized-loopback-bodies.jsonl"
for (let attempt = 0; attempt < 600; attempt++) {
  const count = await readFile(capturePath, "utf8").then((value) => value.trim().split("\n").filter(Boolean).length).catch(() => 0)
  if (count === cases.length) {
    await Promise.all(cases.map(({alias, effort}) => writeFile(process.env.OUTPUT + "/run-" + alias + "-" + effort + ".json", JSON.stringify({status: "request-captured"}, null, 2) + "\n")))
    process.exit(0)
  }
  await new Promise((resolve) => setTimeout(resolve, 100))
}
throw new Error("timed out waiting for eight loopback captures")
JS

python3 - <<'PY'
import json
from pathlib import Path

output = Path("$OUTPUT")
aliases = ("deepseek-v4-flash-fp8-mtp", "deepseek-v4-flash-fp8-mtp-norefusal")
efforts = ("off", "low", "high", "max")
resolved = json.loads((output / "resolved-config.json").read_text())
captures = [json.loads(line) for line in (output / "sanitized-loopback-bodies.jsonl").read_text().splitlines()]
expected = [(alias, effort) for alias in aliases for effort in efforts]
actual = [(item["model"], item["reasoning_effort"]) for item in captures]
assert actual == expected, (actual, expected)
for surface in ("provider", "providers"):
    for alias in aliases:
        variants = resolved[surface]["LiteLLM"]["models"][alias]["variants"]
        ids = list(variants) if isinstance(variants, dict) else [variant["id"] for variant in variants]
        assert ids == list(efforts), (surface, alias, ids)
(output / "assertions.log").write_text(
    "PASS exact ordered captures: both aliases x off, low, high, max\n"
    "PASS exact legacy and V2 variant sets; medium and xhigh absent\n"
    "PASS all eight OpenCode requests reached the loopback mock\n"
)
PY
EOF

printf 'PASS strict loopback harness completed\n'
