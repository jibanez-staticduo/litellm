---
id: TASK-2026-08-15-001-diagnose-fedora-litellm-502
complexity: standard
track: investigation
slice: foundation
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-15-001 - Diagnose Fedora LiteLLM 502

## Objective
Determine why Codex on both the NAS and Fedora receives an OpenResty HTTP 502 from `https://litellm.defend.tech/v1/responses`, and establish whether LiteLLM itself, Docker networking, Nginx Proxy Manager, or the Responses request path is failing.

## Safety And Existing State
- Investigation is read-only; do not restart, recreate, update, or reconfigure containers, proxy hosts, DNS, LiteLLM, Codex, credentials, or source.
- The worktree already contains unrelated user/agent changes in `litellm/proxy/_experimental/mcp_server/server.py`, its test, prior StaticEng task/evidence artifacts, and `.staticeng/tasks/current.md`; preserve them exactly.
- Never print or retain API keys, authorization headers, credentials, request prompts, or response content.

## Acceptance Criteria
- [ ] AC-1: Test health/readiness and `/v1/responses` through both the public OpenResty route and Fedora-local LiteLLM route, using sanitized status/timing evidence.
- [ ] AC-2: Correlate the failing window across Nginx Proxy Manager and LiteLLM container logs and determine whether the request reaches LiteLLM.
- [ ] AC-3: Inspect container health, restart history, resource state, proxy upstream configuration, and relevant timeout/connection behavior without mutation.
- [ ] AC-4: Compare NAS and Fedora Codex endpoint/model configuration without exposing secrets and explain why both clients show the same error.
- [ ] AC-5: Return the root cause or narrowest evidence-backed fault boundary, plus a minimal repair and verification plan.

## Handoff
[Agent Message] From: product_manager To: developer

Perform a read-only production diagnosis on the current NAS and over `ssh fedora`. Start with non-inference probes; if an authenticated Responses probe is needed, use one bounded stateless request with credentials sourced in-place and redact all content. Do not mutate runtime or files. Return the shared output contract with AC-by-AC evidence and explicitly distinguish public proxy behavior from direct localhost behavior.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-5 passed with read-only, sanitized evidence.
- Both LiteLLM containers are healthy; direct Fedora-local health and Responses routing reach LiteLLM normally.
- During the incident, LiteLLM returned HTTP 200 while NPM/OpenResty emitted 502 with `upstream sent too big header while reading response header from upstream`.
- Both Codex clients traverse the same NAS NPM/OpenResty layer, explaining the shared failure.
- Minimal repair is to size Nginx response-header buffers for both LiteLLM proxy hosts or remove the oversized propagated header after size-only inspection.
- Documentation impact: no product documentation update required.
