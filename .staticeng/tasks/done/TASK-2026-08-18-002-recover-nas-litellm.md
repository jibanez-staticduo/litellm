---
id: TASK-2026-08-18-002-recover-nas-litellm
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-08-18-001-diagnose-incomplete-litellm-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-002 - Recover NAS LiteLLM Availability

## Objective
Stop the NAS LiteLLM restart storm by rolling back only the NAS application image to the captured 1.92.0 rollback reference, preserving database, models, credentials, volumes, and Fedora state.

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Safety And Existing State
- Worktree source is clean; only expected `.staticeng/` orchestration changes exist.
- NAS is restarting on the 1.98.0 digest because `/volume2/docker/litellm/patches/mcp_subject_token_optional.py` exits before LiteLLM startup.
- Fedora is healthy on 1.98.0 and must not be changed.
- Do not restore or mutate the database, rebuild/push images, edit source, promote tags, or expose secrets.
- Use only the captured NAS rollback image `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818` and recreate only the NAS LiteLLM service with `--no-deps`.

## Acceptance Criteria
- [ ] AC-1: Capture pre-change NAS image, container state, restart count, OOM state, and a rollback-back reference without secrets.
- [ ] AC-2: NAS LiteLLM is recreated only on the captured 1.92.0 rollback image; no database restore and no dependent service recreation occurs.
- [ ] AC-3: NAS reaches healthy state with readiness and liveliness HTTP 200, stable restart count, and `OOM=false`.
- [ ] AC-4: Runtime reports LiteLLM 1.92.0 and the authenticated model inventory exactly matches the saved 40-model baseline.
- [ ] AC-5: Bounded Responses and LazyMCP smoke probes pass and sanitized startup logs show no release-blocking errors.
- [ ] AC-6: Fedora remains unchanged and healthy on the intended 1.98.0 digest.
- [ ] AC-7: Evidence packet maps AC-1 through AC-6 to results; operational release documentation impact is recorded.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/` with `SUMMARY.md` and non-secret logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Recover NAS availability exactly as scoped. Use the existing rollback artifact and recreate only the NAS LiteLLM service. Preserve database, model inventory, credentials, volumes, and all Fedora state. Stop and report if the rollback reference or 40-model baseline cannot be validated. Return the signed shared output contract with AC-by-AC evidence. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-4 and AC-6 passed; AC-7 evidence and documentation-impact recording are complete
- NAS LiteLLM is healthy on the authorized 1.92.0 rollback image with zero restarts, `OOM=false`, both health endpoints HTTP 200, and an exact 40-model baseline match
- PostgreSQL, Redis, admin MCP dependencies, mounts, protected configuration, credentials, volumes, and Fedora state were preserved
- AC-5 is blocked after three bounded Responses attempts: two 180-second timeouts and one HTTP 400. The dependent LazyMCP smoke was not attempted after the required escalation threshold
- PMA should request Tech Lead assistance to diagnose or disposition the Responses/LazyMCP smoke blocker without disturbing the recovered runtime
- `staticeng_validate` remains blocked by pre-existing repository-wide CodeMap gaps; the repair dry run was not applied because it proposed hundreds of unrelated files
- Product documentation is not required. Operational release closure remains open pending AC-5 resolution or explicit disposition

## Tech Lead: Post Implementation Expectations
- AC-5 is PARTIAL/DISPOSITIONED for availability recovery, not passed.
- The HTTP 400 used an invalid string-input payload; prior valid 1.92.0 Responses checks require list/complex input.
- Both timed-out requests later completed server-side with HTTP 200, establishing provider/fallback latency rather than a rollback startup regression.
- LazyMCP remains unverified and is required in the separate 1.98.0 NAS release retry.
- PMA authorizes closure of availability recovery because AC-1 through AC-4 and AC-6 passed, while the remaining functional checks move explicitly to the release task.
