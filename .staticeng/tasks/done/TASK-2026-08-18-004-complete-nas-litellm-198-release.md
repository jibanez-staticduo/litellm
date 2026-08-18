---
id: TASK-2026-08-18-004-complete-nas-litellm-198-release
complexity: standard
track: implementation
slice: foundation
status: cancelled
scr: null
parent: TASK-2026-08-18-001-diagnose-incomplete-litellm-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-004 - Complete NAS LiteLLM 1.98.0 Release

## Objective
Make the NAS startup wrapper compatible with LiteLLM 1.98.0, redeploy only NAS on the already tested immutable digest, prove full health and functionality, then promote the stable private tag.

## Classification
- **complexity:** standard, decomposed from the overall complex request
- **track:** implementation
- **slice:** foundation

## Safety And Existing State
- NAS is currently recovered and healthy on 1.92.0 with 40 models.
- Fedora is healthy on immutable 1.98.0 digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9` and must remain unchanged.
- Do not rebuild the application image, restore/mutate the database, change models/credentials, or recreate dependency services.
- Back up NAS wrapper/config and preserve a tested 1.92.0 rollback path before changing production.
- Retire the obsolete `mcp_subject_token_optional.py` invocation; compatibility-check the second runtime patch before deciding whether to retain it.
- Prefer aligning NAS startup behavior with the Fedora wrapper that already passed 1.98.0.

## Acceptance Criteria
- [ ] AC-1: Capture current NAS/Fedora states, exact 40-model baseline, protected file hashes, immutable target digest, registry manifest/config identity, and tested rollback references.
- [ ] AC-2: Back up and minimally update the NAS startup wrapper so obsolete host patches cannot block 1.98.0; compatibility-test the rendered wrapper against the target image before production recreation.
- [ ] AC-3: Recreate only NAS LiteLLM with `--no-deps` on the immutable 1.98.0 digest; preserve database, dependencies, volumes, models, credentials, and Fedora state.
- [ ] AC-4: NAS reports version 1.98.0 and target digest/revision, becomes healthy, returns readiness/liveliness HTTP 200, remains at zero restarts with `OOM=false`, and preserves the exact 40-model inventory.
- [ ] AC-5: One known-valid list-input Responses smoke passes with retries disabled and a bounded timeout; sanitized logs prove completion without exposing content.
- [ ] AC-6: LazyMCP status and bounded describe/tool-list smoke pass independently.
- [ ] AC-7: Public LiteLLM routes and a bounded Codex-compatible request pass; sanitized logs show no startup, migration, patch, or release-blocking errors.
- [ ] AC-8: Fedora remains unchanged and healthy on the same 1.98.0 digest.
- [ ] AC-9: Only after AC-1 through AC-8 pass, promote the stable private tag to the verified digest and confirm registry resolution.
- [ ] AC-10: Update the operational release plan with the host-patch compatibility gate and mandatory post-start rollback gate; produce a complete AC-mapped evidence packet.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-004-complete-nas-litellm-198-release/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Complete the NAS-only 1.98.0 release exactly as scoped. Preserve the healthy rollback path and all persistent state. Test wrapper compatibility before recreating production. Do not promote stable until every preceding AC passes. Stop and roll back if health, inventory, Responses, LazyMCP, public route, or Codex validation fails. Update the operational plan and evidence. Do not commit.

# Post Implementation Task Updates

## PMA Cancellation
- Cancelled by direct user instruction before implementation completed.
- No stable-tag promotion was authorized or performed by this task.
- NAS remains on the recovered 1.92.0 runtime pending separate user direction.
