---
id: TASK-2026-08-15-002-expand-npm-litellm-response-buffers
complexity: standard
track: implementation
slice: foundation
status: blocked
scr: null
parent: TASK-2026-08-15-001-diagnose-fedora-litellm-502
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-15-002 - Expand NPM LiteLLM Response Buffers

## Objective
Measure the oversized LiteLLM response-header block and current effective Nginx Proxy Manager limit without retaining header values, then enlarge response buffers with substantial safe margin on both LiteLLM public proxy hosts.

## Safety And Existing State
- Preserve unrelated dirty source, test, and StaticEng changes exactly.
- Use the supported NPM API/MCP for proxy-host updates; do not edit the NPM database directly.
- Never print or retain API keys, authorization headers, cookies, response-header values, prompts, or response content.
- Back up sanitized proxy-host configuration before mutation and preserve all existing advanced directives.

## Acceptance Criteria
- [ ] AC-1: Establish the measured or tightly bounded total/largest response-header size from the failing path, using size-only evidence.
- [ ] AC-2: Establish the current effective `proxy_buffer_size` limit and its source (explicit or platform default).
- [ ] AC-3: Update both LiteLLM public proxy hosts with explicit response buffering that provides substantial margin; preserve existing timeouts and unrelated settings.
- [ ] AC-4: NPM configuration test/reload succeeds and both proxy hosts remain healthy and correctly routed.
- [ ] AC-5: One bounded authenticated stateless `/v1/responses` verification per public hostname returns HTTP 200 and no new oversized-header NPM error; retain no sensitive content.
- [ ] AC-6: Produce `.staticeng/evidences/TASK-2026-08-15-002-expand-npm-litellm-response-buffers/SUMMARY.md` and sanitized logs tracing AC-1 through AC-5; close documentation impact.

## Handoff
[Agent Message] From: product_manager To: developer

Measure sizes only, determine the effective old limit, then update both LiteLLM proxy hosts through supported NPM tooling. Use a generous but bounded configuration, preserving existing directives. Validate Nginx before/after reload and run exactly one sanitized authenticated Responses probe per hostname. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Measured response-header block: 4,452 bytes total; largest field line 445 bytes; previous effective limit 4,096 bytes.
- An initial incomplete buffer update invalidated both NPM hosts; exact prior configurations were restored and public service recovered.
- Reapplied canary-first with the valid complete set: `proxy_buffer_size 32k`, `proxy_buffers 4 32k`, `proxy_busy_buffers_size 64k`.
- Both public readiness checks return HTTP 200; both authenticated stateless Responses probes returned HTTP 200; no new oversized-header errors occurred.
- Evidence packet: `.staticeng/evidences/TASK-2026-08-15-002-expand-npm-litellm-response-buffers/`.
- Documentation impact: no product documentation update required.

## QA Engineer: Post Implementation Expectations

- AC-1 through AC-6 pass.
- Fresh public readiness returned HTTP 200, unauthenticated Responses returned expected HTTP 401, and `nginx -t` passed.
- Both generated host configurations retain expected routing/settings and the complete valid buffer set.
- No authenticated inference was repeated during QA.

## Tech Lead: Post Implementation Expectations

- Technical closure passes; production change is healthy.
- Workflow closure is blocked only by pre-existing repository-wide StaticEng CodeMap debt: 1,779 validation errors and 108 unresolved module-boundary decisions.
- Broad repair is outside this task and was not applied.

## Reopen History

### Reopen 1 - 2026-08-15

- A standalone `proxy_buffer_size 32k` update created an invalid inherited buffer relationship and caused NPM to remove both generated host configurations.
- Rolled both hosts back through the supported API and verified public recovery before further work.
- Technical Architect approved the complete compatible three-directive set.
- Applied host 109 as canary, fully validated it, then applied host 62; both passed authenticated Responses verification.

## Blocker Report

- Production and all task acceptance criteria pass.
- Final StaticEng workflow validation is blocked by unrelated repository-wide CodeMap debt requiring a separate task.

## Reopen History

### 2026-08-15 - Post-change public proxy outage

- After adding only `proxy_buffer_size 32k;` to proxy hosts 62 and 109, NPM removed both generated host configuration files and the public TLS routes stopped matching either hostname
- Both LiteLLM upstreams remained healthy; direct readiness returned HTTP 200 and direct unauthenticated `/v1/responses` returned HTTP 401
- The standalone 32k header buffer exceeded the inherited/default proxy buffer sizing relationship; NPM's update tool reported success even though host generation did not survive validation
- Restored both hosts through the supported authenticated NPM API to their exact sanitized pre-change advanced configurations, including all NAS timeout directives and the Fedora host's empty advanced configuration
- Recovery verification passed: Nginx configuration test succeeded, both generated host files returned, both public readiness probes returned HTTP 200, and both public unauthenticated `/v1/responses` probes returned HTTP 401
- Task remains open; do not retry tuning until a complete compatible `proxy_buffer_size`, `proxy_buffers`, and `proxy_busy_buffers_size` set is validated before mutation

### 2026-08-15 - Architect-approved canary and rollout

- Inspected effective Nginx configuration and found no conflicting global buffer directives or target-host buffer overrides
- Applied the approved complete set to host 109 first: `proxy_buffer_size 32k`, `proxy_buffers 4 32k`, and `proxy_busy_buffers_size 64k`
- Host 109 passed generated-file, directive, server-block, Nginx, readiness, unauthenticated routing, single authenticated Responses, and sanitized error-log checks before host 62 was touched
- Applied the same complete set to host 62 while preserving its existing comments and all four 600-second timeout directives
- Host 62 passed the same checks; both authenticated probes returned HTTP 200 with content discarded and neither host emitted a new oversized-header error
- No `proxy_buffering` directive or unrelated setting was added or changed

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 pass with sanitized evidence under `.staticeng/evidences/TASK-2026-08-15-002-expand-npm-litellm-response-buffers/`
- Both public hosts remain healthy and use the complete architect-approved response-buffer set
- Host 62 retains its comments and 600-second timeouts; host 109 retains no unrelated advanced directives
- Exactly one bounded authenticated stateless Responses probe was performed per hostname after its successful update
- Documentation impact: no product documentation update required; task and operational evidence capture the infrastructure-only change
- Task remains active for PMA review; no registry status or commit was changed
