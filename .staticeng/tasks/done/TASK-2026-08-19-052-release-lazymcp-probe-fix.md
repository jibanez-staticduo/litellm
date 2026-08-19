---
id: TASK-2026-08-19-052-release-lazymcp-probe-fix
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-08-19-048-fix-lazymcp-probe-compatibility
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-052 - Release LazyMCP Probe Fix

## Objective
Build one immutable LiteLLM 1.98.0 image from commit `8589869e1c745ae5c66d96e5475aa816496bc060`, deploy it to Fedora then NAS without automatic rollback, and verify LazyMCP compatibility plus existing release functionality.

## Safety
- Build from an isolated clean checkout/worktree at the exact commit; do not include or alter unrelated uncommitted Fedora StaticEng artifacts in the primary worktree.
- Push only a unique candidate tag initially; promote stable only after both hosts pass.
- Recreate only LiteLLM with `--no-deps`; preserve DB, models, routing, credentials, dependencies, wrappers, mounts, and account3 quarantine.
- Per user instruction, do not automatically roll back. Leave the candidate deployed and diagnose/repair any genuine issue in place.
- Never expose credentials or private request/response content.

## Acceptance Criteria
- [ ] AC-1: Build exactly once from clean commit, linux/amd64, LiteLLM 1.98.0, with matching OCI revision/version and all prior stream/telemetry/cache plus new LazyMCP fixes embedded.
- [ ] AC-2: Focused LazyMCP suites and image-level real SDK checks pass before deployment.
- [ ] AC-3: Fedora and NAS run the same immutable candidate with unchanged topology/dependencies and healthy readiness/liveliness, zero restarts/OOM.
- [ ] AC-4: On both hosts authenticated `HEAD /lazymcp`, generic GET `*/*`, and generic JSON GET return empty 204; SSE GET and MCP POST initialize/tools/list/status/describe/call pass without 405/406.
- [ ] AC-5: Repeated Accept fields, quoted parameters, and q=0 live checks match the approved behavior.
- [ ] AC-6: Existing native Responses/Codex public functionality and LazyMCP harmless tool call pass; release-blocking stream/telemetry/cache/MCP logs are clean over observation.
- [ ] AC-7: After both hosts pass, stable resolves exactly to the candidate digest and host containers remain unchanged by promotion.
- [ ] AC-8: Complete sanitized evidence records build, deployment, live protocol checks, and preservation; no unrelated worktree artifacts are committed.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-052-release-lazymcp-probe-fix/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: developer

Build from an isolated clean checkout at commit `8589869e1c745ae5c66d96e5475aa816496bc060`, deploy Fedora then NAS without automatic rollback, manually diagnose any issue in place, verify all LazyMCP compatibility and existing release gates, then promote stable only after both pass. Preserve unrelated primary-worktree changes. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-8 passed.
- Fedora, NAS, and stable use manifest `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`, version 1.98.0, revision `8589869e1c`.
- All LazyMCP compatibility, protocol, Responses/Codex, preservation, health, and clean-log gates passed without rollback.

## QA Engineer: Final Approval
- Independently approved release closure with AC-1 through AC-6 passing.
- Both hosts retained container IDs/start times across stable promotion, remain healthy, zero restarts/OOM.
- Authenticated compatibility probes return empty 204, unauthorized remain 401, and full MCP/LazyMCP/Responses behavior passes.

## PMA Final Closure
- Release accepted and authorized for repository closure.
- No product or architecture documentation update required.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Built exactly once from a clean detached worktree at the required source commit
- Passed 279 mapped LazyMCP tests, 350 inherited release tests, installed-image checks, and a real MCP SDK repeated-Accept check
- Deployed the same immutable manifest to Fedora and NAS in sequence, recreating only LiteLLM with `--no-deps`
- Diagnosed NAS root registry authentication failure in place and safely used the exact candidate already present in the shared daemon without changing credentials or rolling back
- Passed live HEAD, generic GET, SSE, POST, repeated Accept, quoted parameter, q=0, Responses/Codex, LazyMCP, preservation, health, restart/OOM, and clean-log gates on both hosts
- Promoted stable to the exact candidate manifest only after both hosts passed; promotion did not change either host container
- Created complete sanitized evidence under `.staticeng/evidences/TASK-2026-08-19-052-release-lazymcp-probe-fix/`
- Product, architecture, technical, and CodeMap documentation updates are not required
- Preserved unrelated primary-worktree StaticEng artifacts and created no commit
