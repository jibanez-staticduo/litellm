---
id: TASK-2026-08-19-024-deploy-nas-stream-safe-198
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 4
---

# Task: TASK-2026-08-19-024 - Deploy NAS Stream-Safe 1.98.0

## Objective
Deploy the same verified immutable 1.98.0 candidate to NAS using the migrated wrapper, preserve the new 32-model default/account2 baseline, and execute every functional/preservation gate.

## Safety
- Candidate digest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`.
- Fedora must remain healthy on the same candidate; stable remains untouched until cross-host QA.
- Capture just-in-time credential metadata/log baseline within 60 seconds of deployment using the Tech Lead gate; never read credential contents.
- Preserve the protected 1.92 image plus wrapper/Compose rollback pair and account3 quarantine backup.
- Recreate only NAS `litellm` with `--no-deps`; no DB restore, model/routing/auth mutation, or dependency recreation.
- Roll back NAS image and wrapper/Compose pair on any failure; if release cannot be completed, restore Fedora to avoid split state.

## Acceptance Criteria
- [ ] AC-1: Just-in-time baseline passes with no recent auth/device-flow failure, safe 0700/0600 permissions, exact 32-model/routing hash, dependency identities, and rollback readiness.
- [ ] AC-2: NAS runs the pinned 1.98.0 digest/version/revision through the migrated wrapper; only LiteLLM is recreated.
- [ ] AC-3: Health/readiness/liveliness, restart/OOM, 10-minute observation, startup/schema/migration, and clean-log gates pass.
- [ ] AC-4: Exact 32-model baseline, default primaries, account2 fallbacks/qualified deployments, unrelated routes, protected hashes, credentials metadata, dependencies, volumes, and networks are preserved; account3 remains quarantined.
- [ ] AC-5: Native Responses client `stream=false`, corrected Codex default/account2/public fallback checks pass without stream/auth/device errors and with correct profile selection.
- [ ] AC-6: LazyMCP status, describe, tool-list, and one harmless configured tool smoke pass.
- [ ] AC-7: Fedora remains healthy and unchanged on the same candidate; stable remains unchanged.
- [ ] AC-8: Complete evidence packet records deployment and rollback proof and approves/rejects final cross-host promotion.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-024-deploy-nas-stream-safe-198/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy only NAS by the exact candidate digest using the validated wrapper and strict just-in-time credential gate. Preserve the 32-model default/account2 baseline and quarantined account3 state. Execute every gate, roll back on failure, keep Fedora/stable unchanged, and do not commit.

## Reopen History

### Reopen 1 - 2026-08-19
- Tech Lead proved the first attempts failed only due harness false positives.
- Manifest identity must be checked through deployment reference and RepoDigests against `sha256:42d365...115b`; config identity must compare manifest config digest, local image ID, and running container Image against `sha256:45a019...c73`.
- Never compare running container Image to the manifest digest.
- For only three pre-approved zero-byte credential lock paths, allow ctime to remain equal or advance while requiring exact path/type, non-symlink, owner, mode 0600, size 0, mtime, inode, and device.
- All credential-file, auth/device-flow, functional, preservation, observation, and rollback gates remain unchanged.
- Exactly one controlled redeployment is authorized from verified rollback state.

### Reopen 2 - 2026-08-19
- Tech Lead confirmed Reopen 1 rolled back solely because the harness selected JSON parsing from client `stream=false` despite native provider SSE.
- Exactly one final retry is authorized. Parse by response Content-Type, require `text/event-stream`, blank-line SSE records, valid JSON data events, created/in-progress before exactly one completed event, consistent IDs/sequence, no failure/error/post-completion lifecycle, and no stream/auth/device/unsupported-model errors.
- Preserve all existing identity, credential, topology, LazyMCP, observation, Fedora-isolation, stable, and rollback gates.

### Reopen 3 - 2026-08-19
- Tech Lead classified direct account2 HTTP 429 as external quota/rate limiting and approved one final deployment without requiring account2 HTTP 200.
- Direct account2 must select account2 and return either valid HTTP 200 SSE or provider quota HTTP 429 only, with no auth/device/payload/stream/model/routing/candidate error.
- Public `gpt-5.6-sol` must return HTTP 200 SSE through default primary; native stream=false and direct default must complete valid SSE.
- All identity, 32-model/16-rule hashes, zero account3, LazyMCP, observation, preservation, Fedora/stable isolation, and rollback gates remain mandatory.

### Reopen 4 - 2026-08-19
- Tech Lead classified the opaque observation failure as a harness/evidence defect; no retained evidence establishes a candidate/runtime defect.
- Exactly one final evidence-first deployment is authorized after implementing atomic, attempt-scoped persistence for every observation predicate.
- Persist each container/health/HTTP/restart/OOM/dependency/hash/patch/credential/topology/auth-log/clean-log/identity sub-gate before aggregate evaluation, with expected/actual, pass/fail, identity, artifact path, and hash.
- Capture sanitized candidate logs before rollback; persist aggregate before rollback. Missing evidence fails as `EVIDENCE_INCOMPLETE`, distinct from runtime failure.
- Promotion requires every persisted sub-gate pass; all prior functional and rollback rules remain mandatory.

## Developer: Reopen 4 Final Result
- AC-1 through AC-8 passed.
- NAS runs immutable candidate `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, LiteLLM 1.98.0, revision `b0dfe2e7a7`.
- All 19 atomically persisted observation artifacts and hashes passed.
- Native Responses, direct default, public default-primary, approved account2 quota classification, LazyMCP, exact 32-model/16-rule topology, account3 quarantine, credentials, dependencies, and clean logs passed.
- Fedora and stable remained unchanged during this task.

## PMA Final Closure
- NAS deployment accepted for cross-host completion.
- No steady-state product documentation update is required.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Three fresh just-in-time gates passed before bounded deployment attempts
- Each attempted candidate recreation was stopped by a deployment-harness assertion and automatically rolled back to the protected NAS 1.92.0 image plus wrapper/Compose pair
- The third attempt identified a manifest-versus-config-ID assertion mismatch: manifest `42d365...115b`, NAS-local config ID `45a019...c73`
- Strict credential comparison also found recurring ctime-only drift on one salted lock-file path with every other metadata field unchanged and no correlated auth/device-flow logs
- NAS final rollback health, exact 32-model/routing topology, dependencies, and account3 quarantine pass
- Fedora was restored to its pre-release digest after release failure as required to avoid split state; stable was not changed
- Candidate Responses, Codex, and LazyMCP gates were not run after the mandatory stop
- Cross-host promotion is rejected pending Tech Lead review through PMA
- No product/architecture/CodeMap update is required and no commit was created

## Developer: Reopen 1 Results

- Executed exactly one Tech Lead-authorized controlled NAS redeployment
- Corrected manifest/config/RepoDigests/running identity checks all passed
- Fresh T0, corrected three-lock ctime comparison, health, exact 32-model topology, account3 quarantine, dependencies, mounts, and networks passed
- The first native `stream=false` Responses request returned HTTP 200, then the harness incorrectly attempted JSON parsing instead of accepting the previously documented native event lifecycle
- Applied the mandatory stop before the remaining Codex and LazyMCP gates and automatically restored NAS 1.92.0 plus the protected wrapper/Compose pair
- The rollback passed a 10-minute observation, corrected credential metadata checks, exact topology, dependency, health, and auth-log gates
- Fedora remained unchanged on the Reopen 1 preflight digest; stable remained unresolved and untouched
- Reopen 1 authorization is exhausted, cross-host promotion is rejected, and no further retry was attempted
- No product/architecture/CodeMap update is required and no commit was created

## Developer: Reopen 2 Results

- Executed exactly one final Tech Lead-authorized NAS deployment
- Fresh T0, corrected identity/credential gates, health, exact 32-model topology, account3 quarantine, dependencies, mounts, and networks passed
- Content-Type-driven parsing fully passed the native client `stream=false` SSE gate: HTTP 200, nine valid blank-line JSON events, ordered created/in-progress/completed lifecycle, consistent ID/sequence, one terminal completion, correct profile, and zero forbidden errors
- Direct default Codex passed the same SSE lifecycle and profile assertions
- Direct account2 returned HTTP 429 instead of required HTTP 200, triggering the mandatory stop before public and LazyMCP gates
- Automatically restored NAS 1.92.0 plus the protected wrapper/Compose pair
- Rollback passed a 10-minute observation, corrected credential metadata, exact topology, dependency, health, and auth-log gates
- Fedora remained unchanged; stable remained unresolved and untouched
- Final Reopen 2 authorization is exhausted, cross-host promotion is rejected, and no retry was attempted
- No product/architecture/CodeMap update is required and no commit was created

## Developer: Reopen 3 Results

- Executed exactly one Reopen 3 Tech Lead-authorized NAS deployment
- Fresh T0, corrected identity/credential, immediate health, exact 32-model/16-rule, zero-account3, dependency, mount, and network gates passed
- Native `stream=false`, direct default, and public default-primary each passed HTTP 200 with the exact nine-event SSE lifecycle, correct profile, consistent ID/sequence, one terminal completion, and zero forbidden errors
- Direct account2 passed the Reopen 3 disposition with correctly selected account2 provider-quota HTTP 429 and no other error category
- Full LazyMCP status, describe, exact three-tool list, and harmless `memory-find` smoke passed
- After the ten-minute candidate interval, credential metadata, identity, and exact topology still passed; a later observation aggregate assertion failed without retaining its individual category
- Automatically restored NAS 1.92.0 plus the protected wrapper/Compose pair
- Rollback passed a separate 10-minute observation, credential, topology, health, dependency, and auth-log gates
- Fedora and stable remained unchanged
- Reopen 3 authorization is exhausted, promotion is rejected, and no retry was attempted
- No product/architecture/CodeMap update is required and no commit was created

## Developer: Reopen 4 Results

- Implemented atomic, attempt-scoped, external host persistence before deployment for every required functional/observation sub-gate and aggregate
- Persisted expected/actual, status/classification, container identity, supporting artifact path, and SHA-256 before proceeding; failure semantics distinguish `SUB_GATE_FAILED` from `EVIDENCE_INCOMPLETE`
- Executed exactly one Reopen 4 NAS deployment
- Fresh T0, corrected identity/credential, exact 32-model/16-rule, zero-account3, health, dependency, mount, network, protected-hash, auth-log, and concrete clean-log gates passed
- Native `stream=false`, direct default, allowed direct account2 quota, mandatory public default-primary, and full LazyMCP gates passed
- Completed the candidate 10-minute observation with every persisted sub-gate PASS
- Persisted sanitized candidate-log categories and canonical aggregate before acceptance
- Independently verified all 19 result records and all 19 supporting artifact hashes
- NAS remains healthy on the exact 1.98.0 candidate through the migrated wrapper
- Fedora remained unchanged on the inherited isolation baseline; stable remained unresolved and untouched
- NAS promotion is approved; stable remains held
- No product/architecture/CodeMap update is required and no commit was created
