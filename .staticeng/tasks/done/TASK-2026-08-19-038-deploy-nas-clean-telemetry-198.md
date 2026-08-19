---
id: TASK-2026-08-19-038-deploy-nas-clean-telemetry-198
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-035-build-clean-telemetry-198-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 3
---

# Task: TASK-2026-08-19-038 - Deploy NAS Clean-Telemetry 1.98.0

## Objective
Deploy the same replacement digest to NAS, prove all functional/clean-log gates, and secure the NAS release evidence hierarchy for final cross-host QA.

## Safety
- Fedora remains healthy/unchanged on replacement digest; stable held.
- Recreate only NAS LiteLLM by immutable digest with `--no-deps`; preserve 32-model/default-account2/account3-quarantine topology and all dependencies/state.
- Apply proven identity, credential lock, SSE, quota, public primary, LazyMCP, and atomic observation gates.
- Secure NAS release/evidence/attempt directories to owner-only traversal/write and files to owner-only read/write; preserve hashes and rollback artifacts.
- Roll back on genuine runtime/preservation/security evidence failure.

## Acceptance Criteria
- [ ] AC-1: Fresh baseline/rollback and strict credential metadata gate pass; only NAS LiteLLM is recreated on replacement manifest/config.
- [ ] AC-2: Identity, health, exact 32-model/16-rule topology, zero account3, credentials, dependencies, mounts/networks, and protected hashes pass.
- [ ] AC-3: Native/default/public Responses and approved account2 quota gate, corrected Codex SSE, and full LazyMCP matrix pass.
- [ ] AC-4: Ten-minute observation spans multiple cache polls with zero telemetry/cache/release-blocking tracebacks.
- [ ] AC-5: NAS release/evidence hierarchy is non-world-writable, directories owner-only, artifacts owner-only, hash chain reverified after permission hardening.
- [ ] AC-6: Fedora remains healthy/unchanged on same replacement digest; stable held.
- [ ] AC-7: Complete evidence approves/rejects final cross-host QA.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-038-deploy-nas-clean-telemetry-198/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy only NAS by the replacement digest, execute every proven functional/preservation/clean-log gate, and secure/reverify NAS evidence permissions and hashes. Preserve Fedora/stable. Roll back on genuine failure. Do not commit.

## Reopen History

### Reopen 1 - 2026-08-19
- Three attempts stopped pre-deployment due harness assumptions; no NAS mutation occurred.
- Treat `op_service_account_token` as root-owned empty 0755 directory; preserve metadata/tree projection and exact read-only bind tuple while hashing four protected regular files.
- Inspect only literal `chatgpt-auth` and `anthropic-auth`: root-owned 0700 dirs, direct root-owned 0600 regular files, zero-byte lock ctime monotonic only.
- Fedora isolation uses pinned `staticduo@fedora-ssh.staticduo.com`, asserting user `staticduo` UID 1000 and exact container/mount/network metadata.
- Corrected harness must pass `bash -n`; exactly one attempt approved.

## Blocker Report
- Private registry Docker config exists for `staticduo` but its directory/file modes are 0777.
- Candidate is already present in the shared daemon with exact identity, but deployment retry is blocked until Docker credential metadata is hardened and reverified.

## Reopen History

### Reopen 2 - 2026-08-19
- NAS Docker credential directory/file were hardened to 0700/0600 with ownership/size/mtime/inode preserved and access verified.
- Exact replacement candidate is already present in the shared daemon and visible to `staticduo` and root with matching manifest/config/platform.
- Skip registry pull when exact local identity assertions pass; execute the complete fail-closed deployment gate.

### Reopen 3 - 2026-08-19
- User explicitly prohibited further automatic rollback.
- Deploy the replacement digest and leave it running.
- If a check fails, persist its exact evidence, inspect it manually, and repair the real issue in place; do not treat combined harness assertions as rollback triggers.
- Preserve rollback artifacts for emergency reference only. Do not use them without a separate explicit instruction.
- Completion still requires health, public/default functionality, expected account2 quota classification, LazyMCP, topology, telemetry/cache clean logs, Fedora alignment, and secured evidence.

## Developer: Reopen 3 Final Result
- AC-1 through AC-7 passed.
- NAS runs replacement manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3` healthy with zero restarts/OOM.
- Native/default/account2/public all passed HTTP 200 native SSE with correct selection; LazyMCP passed.
- Exact 32 models, 16 rules, and zero account3 preserved.
- 600-second/21-poll observation found zero telemetry/cache/stream release blockers.
- Evidence hierarchy is secured and reverified; Fedora remains on the same replacement digest; stable held.

## PMA Final Closure
- NAS replacement deployment accepted under the user's no-rollback instruction.
- No product or architecture documentation update required.

# Post Implementation Task Updates

## Developer: Reopen 1 Results

- Incorporated every Tech Lead corrected gate and passed `bash -n`
- Executed exactly one approved attempt, `nas-clean-20260819T043340Z`
- Fresh protected-directory, read-only bind, literal credential-root, exact topology, Fedora isolation, stable, and rollback baselines passed
- Root candidate acquisition failed because that execution context had no private-registry credentials
- Failure occurred before changing `LITELLM_IMAGE`, recreating NAS LiteLLM, or sending functional probe traffic
- NAS remained healthy on prior manifest `42d36549...115b`; Fedora remained healthy and unchanged on replacement manifest `35fc5209...f2d3`; stable remained unchanged/missing
- Hardened the full retained NAS release/evidence hierarchy to root-owned 0700 directories and 0600 files and reverified its complete hash chain
- Reopen 1 authorization is exhausted and final cross-host QA is rejected pending PMA/Tech Lead disposition
- No product, architecture, technical, or CodeMap documentation update is required; no commit was created

## Developer: Reopen 2 Results

- Verified hardened Docker credential metadata and byte-identical root/staticduo exact local candidate identity, then correctly skipped registry pull
- Executed one complete fail-closed deployment attempt and recreated only NAS LiteLLM with `--no-deps`
- Replacement manifest/config identity and immediate health passed
- Native `stream=false`, direct-default, and approved account2 probes passed sequential assertions
- Mandatory public default-primary failed the combined selection-or-blocked-error predicate; the response was not retained, so the narrower category is unavailable
- Applied the mandatory stop before LazyMCP and candidate observation and automatically restored prior manifest `42d36549...115b`
- Rollback passed a separate 600-second/21-poll health, exact topology, credential, dependency, mount/network, protected-hash, Fedora-isolation, and stable-hold verification
- The restored prior image continues to emit its inherited usage-cache NameError tracebacks
- Hardened the complete NAS release/evidence hierarchy to root-owned 0700 directories and 0600 files and reverified the hierarchy hash chain
- Reopen 2 is exhausted; final cross-host QA is rejected pending PMA/Tech Lead review
- No product, architecture, technical, or CodeMap update is required; no commit was created

## Developer: Reopen 3 Results

- Applied the user's direct no-rollback override and left exact replacement manifest `35fc5209...f2d3` running on NAS
- Recreated only NAS LiteLLM with `--no-deps`; identity, health, restart/OOM, dependency, mount/network, protected-state, and rollback-artifact gates passed
- Persisted separate HTTP status, SSE lifecycle, blocked-error, quota, provider-profile, and deployment-selection evidence for every probe
- Native `stream=false`, direct default, direct account2, and public default-primary each returned HTTP 200 with a complete nine-event SSE lifecycle and correct selection
- Proved the prior public rejection was a harness expectation defect: the public route has its own deployment ID while using default provider model `chatgpt/gpt-5.6-sol`
- Full LazyMCP passed with current configured identifiers `Memory` / `memory-find`; prior identifiers were stale probe assumptions
- Completed at least 600 seconds and 21 polls on the same healthy replacement container with zero telemetry, usage-cache, stream, auth/device, migration/schema/patch release-blocking findings
- Exact 32-model/16-rule, eight-default/eight-account2, zero-account3 topology, credential metadata, dependencies, mounts/networks, non-image environment, and protected hashes passed
- Fedora remained healthy and unchanged on the same replacement digest; stable remained unchanged/missing
- Hardened the complete NAS release/evidence hierarchy to root-owned 0700 directories and 0600 files and reverified the complete hash chain
- AC-1 through AC-7 pass; approve final cross-host QA while stable remains held
- No product, architecture, technical, or CodeMap documentation update is required; no commit was created
