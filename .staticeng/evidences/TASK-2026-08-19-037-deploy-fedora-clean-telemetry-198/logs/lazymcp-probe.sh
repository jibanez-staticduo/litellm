#!/usr/bin/env bash
set -euo pipefail

stack=/home/staticduo/docker/litellm
set -a
. "$stack/.env"
set +a

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

request() {
  local id=$1
  local method=$2
  local params=$3
  local output=$4
  local payload="$tmp_dir/request-${id}.json"

  jq -n --argjson id "$id" --arg method "$method" --argjson params "$params" \
    '{jsonrpc: "2.0", id: $id, method: $method, params: $params}' > "$payload"

  curl --max-time 120 --retry 0 -fsS \
    -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -H 'MCP-Protocol-Version: 2025-11-25' \
    --data-binary "@$payload" \
    http://127.0.0.1:4000/lazymcp > "$output"
}

normalize() {
  local input=$1
  local output=$2
  python3 - "$input" "$output" <<'PY'
import json
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_text()
data_lines = [line.removeprefix("data:").strip() for line in raw.splitlines() if line.startswith("data:")]
payload = json.loads(data_lines[-1] if data_lines else raw)
Path(sys.argv[2]).write_text(json.dumps(payload, sort_keys=True))
PY
}

request 1 tools/list '{}' "$tmp_dir/list.raw"
normalize "$tmp_dir/list.raw" "$tmp_dir/list.json"
tool_names=$(jq -r '.result.tools | map(.name) | sort | join(",")' "$tmp_dir/list.json")
test "$tool_names" = 'mcp_call,mcp_describe,mcp_status'
printf 'protocol=2025-11-25 tools=%s\n' "$tool_names"

request 2 tools/call '{"name":"mcp_status","arguments":{}}' "$tmp_dir/status.raw"
normalize "$tmp_dir/status.raw" "$tmp_dir/status.json"
jq -e '.error == null and .result.isError != true' "$tmp_dir/status.json" >/dev/null
printf 'mcp_status=pass\n'

request 3 tools/call '{"name":"mcp_describe","arguments":{"server":"defend_memory","tool":"defend_memory-find"}}' "$tmp_dir/describe.raw"
normalize "$tmp_dir/describe.raw" "$tmp_dir/describe.json"
jq -e '.error == null and .result.isError != true' "$tmp_dir/describe.json" >/dev/null
grep -q 'defend_memory-find' "$tmp_dir/describe.json"
printf 'mcp_describe_defend_memory_find=pass\n'

request 4 tools/call '{"name":"mcp_call","arguments":{"server":"defend_memory","tool":"defend_memory-find","arguments":{"query":"TASK-2026-08-19-037 harmless validation"}}}' "$tmp_dir/call.raw"
normalize "$tmp_dir/call.raw" "$tmp_dir/call.json"
jq -e '.error == null and .result.isError != true' "$tmp_dir/call.json" >/dev/null
printf 'mcp_call_defend_memory_find=pass\n'
