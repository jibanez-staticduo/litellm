#!/usr/bin/env bash
set -euo pipefail

stack=/home/staticduo/docker/litellm
set -a
. "$stack/.env"
set +a

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

curl -fsS \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  http://127.0.0.1:4000/model/info > "$tmp_dir/model-info.json"

account2_id=$(jq -r '[.data[] | select(.model_name == "chatgpt-account2/gpt-5.6-sol") | .model_info.id][0]' "$tmp_dir/model-info.json")
test -n "$account2_id"
test "$account2_id" != null

run_probe() {
  local label=$1
  local model=$2
  local stream=$3
  local payload="$tmp_dir/${label}-payload.json"
  local headers="$tmp_dir/${label}-headers.txt"
  local body="$tmp_dir/${label}-body.txt"
  local status
  local content_type
  local selected
  local completed
  local failed
  local selected_account2

  jq -n --arg model "$model" --argjson stream "$stream" '{
    model: $model,
    input: [{role: "user", content: [{type: "input_text", text: "Reply with exactly OK."}]}],
    reasoning: {context: "all_turns", effort: "high", summary: "detailed"},
    stream: $stream,
    store: false,
    include: ["reasoning.encrypted_content"],
    parallel_tool_calls: false
  }' > "$payload"

  status=$(curl --max-time 180 --retry 0 -sS \
    -D "$headers" \
    -o "$body" \
    -w '%{http_code}' \
    -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
    -H 'Content-Type: application/json' \
    -H 'x-openai-internal-codex-responses-lite: true' \
    --data-binary "@$payload" \
    http://127.0.0.1:4000/v1/responses)

  content_type=$(tr -d '\r' < "$headers" | grep -i '^content-type:' | tail -n1 | cut -d' ' -f2-)
  selected=$(tr -d '\r' < "$headers" | grep -i '^x-litellm-model-id:' | tail -n1 | cut -d' ' -f2-)
  completed=$(grep -o 'response.completed' "$body" | wc -l)
  failed=$(grep -Eic 'response.failed|Stream must be set to true|Authentication required|device flow|unsupported_value|unsupported_model' "$body" || true)
  if test "$selected" = "$account2_id"; then
    selected_account2=true
  else
    selected_account2=false
  fi

  printf '%s status=%s content_type=%s completed=%s blocked_errors=%s selected_account2=%s\n' \
    "$label" "$status" "$content_type" "$completed" "$failed" "$selected_account2"
}

run_probe native_account2_stream_false chatgpt-account2/gpt-5.6-sol false
run_probe qualified_regular chatgpt/gpt-5.6-sol true
run_probe direct_account2 chatgpt-account2/gpt-5.6-sol true
run_probe public_fallback gpt-5.6-sol true
