#!/bin/sh
set -eu

export HOME=/work/home
export XDG_CONFIG_HOME=/work/config
export XDG_DATA_HOME=/work/data
export XDG_CACHE_HOME=/work/cache
export XDG_STATE_HOME=/work/state
export OPENCODE_CONFIG_DIR=/work/config/opencode
export OPENCODE_DATA_DIR=/work/data/opencode
export OPENCODE_CACHE_DIR=/opencode-cache
export OPENCODE_STATE_DIR=/work/state/opencode
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost

mkdir -p "$HOME" "$OPENCODE_CONFIG_DIR" "$OPENCODE_DATA_DIR" "$OPENCODE_STATE_DIR"
cat > "$XDG_CONFIG_HOME/opencode/opencode.json" <<'JSON'
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [[
    "file:///plugin/dist/index.js",
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
  echo "docker_network_mode=none"
  echo "opencode_version=$(opencode-host --version)"
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
socket.on("error", (error) => { console.log(`external_connect=blocked code=${error.code}`); process.exit(0) })
socket.on("timeout", () => { console.log("external_connect=blocked timeout"); socket.destroy(); process.exit(0) })
JS
} > /output/network-isolation.log

python3 /harness/mock_server.py /output/sanitized-loopback-bodies.jsonl >/output/mock-server.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT

attempt=0
until curl --silent --fail http://127.0.0.1:18765/model_group/info >/dev/null; do
  attempt=$((attempt + 1))
  [ "$attempt" -lt 50 ] || exit 1
  sleep 0.1
done

opencode-host debug config >/output/resolved-config.json
for alias in deepseek-v4-flash-fp8-mtp deepseek-v4-flash-fp8-mtp-norefusal; do
  for effort in off low high max; do
    opencode-host run --format json --title strict-loopback --model "LiteLLM/$alias" --variant "$effort" \
      "fixture prompt for strict loopback capture" >"/output/run-$alias-$effort.jsonl"
  done
done

python3 - <<'PY'
import json
from pathlib import Path

aliases = ("deepseek-v4-flash-fp8-mtp", "deepseek-v4-flash-fp8-mtp-norefusal")
efforts = ("off", "low", "high", "max")
resolved = json.loads(Path("/output/resolved-config.json").read_text())
captures = [json.loads(line) for line in Path("/output/sanitized-loopback-bodies.jsonl").read_text().splitlines()]
expected = [(alias, effort) for alias in aliases for effort in efforts]
actual = [(item["model"], item["reasoning_effort"]) for item in captures]
assert actual == expected, (actual, expected)
for surface in ("provider", "providers"):
    for alias in aliases:
        variants = resolved[surface]["LiteLLM"]["models"][alias]["variants"]
        ids = list(variants) if isinstance(variants, dict) else [variant["id"] for variant in variants]
        assert ids == list(efforts), (surface, alias, ids)
Path("/output/assertions.log").write_text(
    "PASS exact ordered captures: both aliases x off, low, high, max\n"
    "PASS exact legacy and V2 variant sets; medium and xhigh absent\n"
    "PASS all inference responses completed from loopback mock\n"
)
PY
