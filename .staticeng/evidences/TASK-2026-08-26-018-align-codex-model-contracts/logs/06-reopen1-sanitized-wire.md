# Reopen 1 Sanitized Responses Captures

Codex `0.149.1` executed ephemeral strict-config runs against an isolated `CODEX_HOME` and loopback-only `127.0.0.1` Responses capture server. The isolated config used a placeholder credential helper, zero retries, and the production custom catalog. Captures retained only path, model, effort, input presence, and authorization-header presence; they retained no prompt/input, body, response content, headers, or credential value

All 45 distinct catalog row/mode combinations passed:

```text
gpt-5.3-codex-spark: none,low,medium,high,xhigh
gpt-5.4: none,low,medium,high,xhigh
gpt-5.4-mini: none,low,medium,high,xhigh
gpt-5.5: none,low,medium,high,xhigh
gpt-5.6-luna: none,low,medium,high,xhigh,max
gpt-5.6-sol: none,low,medium,high,xhigh,max
gpt-5.6-terra: none,low,medium,high,xhigh,max
deepseek-v4-flash-fp8-mtp: none,low,high,max
qwen3.8-27b-refusal-dial: low,medium,xhigh
```

Five ordered row-switch captures also passed:

```text
deepseek-v4-flash-fp8-mtp/high
qwen3.8-27b-refusal-dial/xhigh
gpt-5.4/none
deepseek-v4-flash-fp8-mtp/none
qwen3.8-27b-refusal-dial/low
```

Each request used `/v1/responses`, contained input, carried authorization presence, and transmitted exactly the selected row's effort. This proves the active global DeepSeek `high` does not leak when switching to Qwen or GPT and that subsequent switches replace prior row efforts. Total captures: 50. Production inference requests: zero
