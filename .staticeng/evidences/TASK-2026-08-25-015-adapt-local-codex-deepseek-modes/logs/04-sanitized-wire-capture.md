# Sanitized Responses Wire Capture

Four `codex exec --strict-config --ephemeral` runs used an isolated `CODEX_HOME`, a loopback-only HTTP capture endpoint at `127.0.0.1:18425`, a placeholder credential, zero retries, and the production catalog. The isolated config did not contain or contact the production URL. The capture retained only endpoint path, model, selected effort, input presence, and authorization-header presence; it did not retain prompt/input, full bodies, headers, or credential values

```json
[
  {"path":"/v1/responses","model":"deepseek-v4-flash-fp8-mtp","reasoning_effort":"off","has_input":true,"authorization_present":true},
  {"path":"/v1/responses","model":"deepseek-v4-flash-fp8-mtp","reasoning_effort":"low","has_input":true,"authorization_present":true},
  {"path":"/v1/responses","model":"deepseek-v4-flash-fp8-mtp","reasoning_effort":"high","has_input":true,"authorization_present":true},
  {"path":"/v1/responses","model":"deepseek-v4-flash-fp8-mtp","reasoning_effort":"max","has_input":true,"authorization_present":true}
]
```

Assertion passed: emitted efforts equal `[off, low, high, max]` in order. The app-server selector assertion separately proves `medium` and `xhigh` are absent and therefore cannot be selected for the target. No production inference occurred
