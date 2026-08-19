# Reopen 2 Final Controlled Attempt

## Preflight And Recreation

- Final one-attempt authorization: verified
- Fresh T0: `2026-08-19T01:16:38Z`
- Prior 15-minute auth/device-flow failure matches: 0
- Manifest/RepoDigests: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Registry config/local image/running image ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Candidate architecture/version/revision: amd64 / 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Corrected credential gate: PASS; one approved lock path advanced only ctime
- Exact 32-model, 16-rule, default/account2, public-primary, and account3-quarantine gates: PASS
- Dependencies, mounts, networks, health, readiness, liveliness, restart, and OOM gates: PASS
- Mutation scope: `LITELLM_IMAGE` plus only NAS `litellm` recreation with `--no-deps`

## Content-Type-Driven Native SSE Gate

Client request specified `stream=false`. Parsing selected SSE from response `Content-Type`, not the request flag

- HTTP status: 200
- Content-Type: `text/event-stream`
- Blank-line-delimited SSE records: PASS
- Valid JSON data events: 9
- `response.created` then `response.in_progress` before exactly one `response.completed`: PASS
- Consistent response ID and contiguous event sequence: PASS
- Failure/error/incomplete/cancelled events: 0
- Post-completion lifecycle events: 0
- Stream/auth/device/unsupported-model errors: 0
- Correct default deployment selection: PASS

## Corrected Codex Gates

- Direct default `chatgpt/gpt-5.6-sol`: HTTP 200 SSE, nine valid events, full ordered lifecycle, consistent ID/sequence, exactly one completion, correct default deployment, PASS
- Direct account2 `chatgpt-account2/gpt-5.6-sol`: HTTP 429, FAIL mandatory success condition
- Public `gpt-5.6-sol`: not reached after mandatory stop
- LazyMCP matrix: not reached after mandatory stop

Exactly one Reopen 2 attempt was made. No retry followed

Result: **REJECT ON ACCOUNT2 HTTP 429**
