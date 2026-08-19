#!/usr/bin/env bash
set -Eeuo pipefail

readonly ROOT=/volume2/docker/litellm/releases/20260819-clean-telemetry-198-deploy
readonly ATTEMPT=$(cat "$ROOT/reopen3-current-attempt.txt")

docker exec -i litellm python - >"$ATTEMPT/functional-gates.json" <<'PY'
import hashlib
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
by_name = {row["model_name"]: row for row in rows}
default_id = by_name["chatgpt/gpt-5.6-sol"]["model_info"]["id"]
account2_id = by_name["chatgpt-account2/gpt-5.6-sol"]["model_info"]["id"]
public_id = by_name["gpt-5.6-sol"]["model_info"]["id"]
public_provider_model = by_name["gpt-5.6-sol"]["litellm_params"]["model"]

def probe(label, model, stream, expected_id, allow_quota=False):
    payload = json.dumps({"model":model,"input":[{"role":"user","content":[{"type":"input_text","text":"Reply with exactly OK."}]}],"reasoning":{"context":"all_turns","effort":"high","summary":"detailed"},"stream":stream,"store":False,"include":["reasoning.encrypted_content"],"parallel_tool_calls":False}).encode()
    request = urllib.request.Request(base + "/v1/responses", data=payload, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=180)
        status, response_headers, body = response.status, response.headers, response.read().decode(errors="replace")
    except urllib.error.HTTPError as error:
        status, response_headers, body = error.code, error.headers, error.read().decode(errors="replace")
    selected = response_headers.get("x-litellm-model-id", "")
    blocked_markers = ("Stream must be set to true", "Authentication required", "device flow", "unsupported_value", "unsupported_model", "response.failed")
    blocked = sorted(marker for marker in blocked_markers if marker.lower() in body.lower())
    quota = any(marker in body.lower() for marker in ("quota", "rate", "429", "too many"))
    events = []
    if response_headers.get_content_type().startswith("text/event-stream"):
        for record in body.replace("\r\n", "\n").split("\n\n"):
            data = "\n".join(line[5:].strip() for line in record.splitlines() if line.startswith("data:"))
            if data and data != "[DONE]":
                try:
                    events.append(json.loads(data))
                except json.JSONDecodeError:
                    events.append({"type": "invalid_json"})
    types = [event.get("type") for event in events]
    lifecycle = status == 200 and response_headers.get_content_type().startswith("text/event-stream") and types.count("response.created") == 1 and types.count("response.in_progress") == 1 and types.count("response.completed") == 1 and types[-1:] == ["response.completed"]
    status_gate = status == 200 or allow_quota and status == 429 and quota
    return {"label":label,"http_status":status,"status_gate":status_gate,"content_type":response_headers.get_content_type(),"sse_lifecycle_gate":lifecycle if status == 200 else None,"event_count":len(events),"blocked_error_gate":not blocked,"blocked_categories":blocked,"quota_classification":quota if status == 429 else None,"selected_id":selected,"expected_id":expected_id,"selection_gate":selected == expected_id,"body_sha256":hashlib.sha256(body.encode()).hexdigest()}

results = [
    probe("native_stream_false", "chatgpt/gpt-5.6-sol", False, default_id),
    probe("direct_default", "chatgpt/gpt-5.6-sol", True, default_id),
    probe("direct_account2", "chatgpt-account2/gpt-5.6-sol", True, account2_id, True),
    probe("public_default_primary", "gpt-5.6-sol", True, public_id),
]
print(json.dumps({"public_provider_model":public_provider_model,"public_provider_is_default":public_provider_model.startswith("chatgpt/") and not public_provider_model.startswith("chatgpt-account2/"),"results":results},sort_keys=True))
PY
chmod 600 "$ATTEMPT/functional-gates.json"
chown root:root "$ATTEMPT/functional-gates.json"
jq '{public_provider_model:.public_provider_model,public_provider_is_default:.public_provider_is_default,results:[.results[]|{probe:.label,http_status:.http_status,status_gate:.status_gate,content_type:.content_type,sse_lifecycle_gate:.sse_lifecycle_gate,event_count:.event_count,blocked_error_gate:.blocked_error_gate,blocked_categories:.blocked_categories,quota_classification:.quota_classification,selection_gate:.selection_gate}]}' "$ATTEMPT/functional-gates.json"
