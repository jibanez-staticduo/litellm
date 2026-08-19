# Sanitized Verification

## Preflight

- NAS LiteLLM: running and healthy
- Restart count: 0
- OOM killed: false
- Model rows: 32
- Account3 topology references: 0
- Explicit profile target: account3
- Account3 authorization processes: 0
- Account3 profile lock: available
- Credential metadata safety gate: passed

## Post-start

- Supported account3 device authorization invocation count: 1
- Active account3 authorization processes: 1
- Account3 profile lock: held
- NAS LiteLLM: running and healthy
- Restart count: 0
- OOM killed: false
- Model rows: 32
- Account3 topology references: 0

No container restart/recreation, routing/model mutation, credential-content inspection, token output, or transient authorization detail was persisted

## Post-authorization metadata

- Account3 authorization processes: 0
- Account3 profile lock: available
- Explicit credential target: account3
- Credential file: root-owned regular non-symlink, mode 0600
- Credential modification time: after device-flow start
- Credential contents: not exposed or persisted

## Bounded direct account3 probe

- Request count: 1
- Retries: 0
- API: Responses, direct provider path
- Model: gpt-5.6-sol
- Explicit selected profile: account3
- Known-valid Codex-compatible payload: used
- HTTP status: 200
- Upstream Content-Type header: absent
- SSE event count: 9
- Lifecycle: response.created -> response.in_progress -> output item/content/text events -> response.completed
- response.created count: 1
- response.in_progress count: 1
- response.completed count: 1
- response.failed count: 0
- Error event count: 0
- Sanitized provider/auth error category: none

## Post-probe preservation

- NAS LiteLLM: running and healthy
- Image and container start time: unchanged
- Restart count: 0
- OOM killed: false
- Model rows: 32
- Account3 topology references: 0
- Account3 credential metadata and modification time: unchanged by the probe

No deployment/fallback restoration, service restart/recreation, routing/model/config/database/tag/source mutation, secret persistence, or commit occurred
