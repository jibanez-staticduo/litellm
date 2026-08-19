#!/usr/bin/env bash
set -Eeuo pipefail

readonly ROOT=/volume2/docker/litellm/releases/20260819-clean-telemetry-198-deploy
readonly ATTEMPT=$(cat "$ROOT/reopen3-current-attempt.txt")

docker exec -i litellm python - >"$ATTEMPT/lazymcp-gates.json" <<'PY'
import json
import os
import urllib.request

url = "http://127.0.0.1:4000/lazymcp"
headers = {"Authorization":"Bearer " + os.environ["LITELLM_MASTER_KEY"],"Content-Type":"application/json","Accept":"application/json, text/event-stream","MCP-Protocol-Version":"2025-11-25"}

def call(identifier, method, params):
    request = urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":identifier,"method":method,"params":params}).encode(),headers=headers)
    raw = urllib.request.urlopen(request,timeout=120).read().decode()
    lines = [line.removeprefix("data:").strip() for line in raw.splitlines() if line.startswith("data:")]
    result = json.loads(lines[-1] if lines else raw)
    return result, not result.get("error") and result.get("result",{}).get("isError") is not True

listed, list_gate = call(1,"tools/list",{})
tools = sorted(tool["name"] for tool in listed.get("result",{}).get("tools",[]))
status, status_gate = call(2,"tools/call",{"name":"mcp_status","arguments":{}})
described, describe_gate = call(3,"tools/call",{"name":"mcp_describe","arguments":{"server":"Memory","tool":"memory-find"}})
smoke, smoke_gate = call(4,"tools/call",{"name":"mcp_call","arguments":{"server":"Memory","tool":"memory-find","arguments":{"query":"TASK-2026-08-19-038 reopen3 harmless validation"}}})
print(json.dumps({"protocol":"2025-11-25","tool_list_gate":list_gate and tools == ["mcp_call","mcp_describe","mcp_status"],"tools":tools,"status_gate":status_gate,"server":"Memory","tool":"memory-find","describe_gate":describe_gate and "memory-find" in json.dumps(described),"smoke_gate":smoke_gate},sort_keys=True))
PY
chmod 600 "$ATTEMPT/lazymcp-gates.json"
chown root:root "$ATTEMPT/lazymcp-gates.json"
jq . "$ATTEMPT/lazymcp-gates.json"
