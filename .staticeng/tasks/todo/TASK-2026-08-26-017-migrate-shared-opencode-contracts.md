---
id: TASK-2026-08-26-017-migrate-shared-opencode-contracts
complexity: complex
track: implementation
slice: core
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 6
---

# Task: TASK-2026-08-26-017 - Migrate Shared OpenCode Contracts

## Objective
Atomically clean known-model overrides from the NAS-authoritative Syncthing-shared OpenCode configuration and prove official OpenCode loads published plugin 0.2.0 across synchronized hosts.

## Acceptance Criteria
- [ ] T3-AC-1: Fresh protected NAS backup and redacted structural baseline prove exactly approved known/retired/defend override keys are removed; all unrelated paths and protected hashes remain unchanged.
- [ ] T3-AC-2: Plugin reference remains exact unversioned `@staticeng/opencode-litellm`, JSON parses, mode remains `0600`, and zero local/file references exist.
- [ ] T3-AC-3: NAS is the only direct writer; Syncthing reaches idle/up-to-date convergence on every expected peer with matching checksums and no conflict files.
- [ ] T3-AC-4: On each reachable synchronized host, invalidate only stale `@staticeng/opencode-litellm` cache state and prove a fresh official OpenCode process resolves installed version `0.2.0`; do not edit peer config.
- [ ] T3-AC-5: Record fresh process/version evidence without terminating the rollout control session or unrelated user sessions; identify any pre-existing processes that require user restart.
- [ ] T3-AC-6: Official OpenCode exposes exact approved named modes for every discovered known alias, no normal GPT-5.3 or defend entry, preserved Spark, and no fabricated aliases.
- [ ] T3-AC-7: Strict isolated captures prove each distinct contract row/default, alias equivalence, intrinsic Default omission, and user-last override precedence.
- [ ] T3-AC-8: Complete evidence contains no credentials, prompts, responses, or unredacted config.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/` with `SUMMARY.md` and redacted logs/screenshots where useful.

## Rollback
Restore the exact NAS backup atomically from NAS only, wait for Syncthing convergence, invalidate only plugin cache, and prove prior behavior. Emergency package pin to `@0.1.9` requires blocker evidence.

## Stop Conditions
Stop on unexpected path changes, secret exposure, Syncthing conflict/divergence, package version mismatch, selector/payload failure, or inability to identify/protect active sessions.

## Reopen History

### Reopen 1 - 2026-08-26
- Initial all-peer preflight found 6 connected/complete and 6 offline/incomplete peers, so no mutation occurred.
- User approved immediate scope as NAS plus every currently connected expected peer.
- Offline peers remain untouched and will receive the authoritative NAS file automatically on reconnect; record them as eventual-convergence follow-up.
- Fresh preflight found five of six connected expected peers at 100% completion; one connected expected peer remained below 100% after bounded NAS and peer scans.
- The connected-peer convergence stop condition was enforced before configuration inspection, backup, cache invalidation, or process changes.

### Reopen 2 - 2026-08-26
- The sole connected-peer divergence was repaired through authorized backup and Syncthing receive-only revert on cachyos.
- Connected peer now reports 100%, zero pending items/errors/conflicts, aligned sequences, and stable bounded scan.
- Resume full migration from fresh preflight.

### Reopen 3 - 2026-08-26
- Six standard Syncthing conflict artifacts on non-NAS Fedora were deleted under the user-approved standing NAS-wins policy.
- Fresh verification reported all six connected peers at 100%, zero needed items/bytes/deletes, zero conflicts/errors, and matching authoritative `opencode.json`.
- A protected mode-`0600` exact backup was created outside the synchronized tree, and the NAS-only atomic candidate removed exactly the 25 approved GPT/retired/defend overrides while preserving all unrelated structure.
- A seventh expected peer connected during post-mutation convergence, remained one item behind through the bounded wait, and disconnected.
- The post-mutation convergence stop condition triggered exact atomic rollback from NAS before any cache invalidation, process launch, or behavior matrix.
- Post-rollback NAS and the six remaining connected peers match the prior checksum, are 100% complete and conflict-free, and no peer was directly edited.

### Reopen 4 - 2026-08-26
- User clarified convergence is evaluated against the stable connected set at the end of the bounded window; transient disconnected peers are future convergence and are not alone a rollback trigger.
- Fresh preflight and the exact NAS-only candidate passed; all six final connected peers converged to the candidate at 100% with matching checksums and zero conflicts.
- Only stale unversioned plugin package cache state was invalidated on NAS and six reachable connected hosts.
- Fresh official OpenCode `1.18.23` failed to initialize published plugin `0.2.0` with a discovery-response type error and could not prove an installed `0.2.0` runtime.
- The package/behavior stop condition triggered exact atomic NAS rollback before selector or wire matrix execution.
- Post-rollback NAS and all six connected peers match the prior checksum, are 100% complete and conflict-free; no process was terminated and no peer configuration was directly edited.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Read-only Syncthing preflight found the NAS authoritative folder idle and error-free, but only 6 of 12 expected peers were at 100% completion
- Six expected peers were offline and six were below 100% completion, including one connected stale peer; the required all-peer convergence gate therefore failed
- Execution stopped before reading or backing up `opencode.json`, inspecting protected values, editing any host, invalidating cache, or changing processes
- No rollback was required because mutation count was zero
- Redacted blocker evidence is under `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/`
- Product and architecture documentation are not required for this blocked preflight
- `staticeng_validate` remains blocked by the pre-existing repository-wide manual CodeMap backlog; mandatory repair dry-run and apply found no deterministic fix
- Reopen 1 applied the user-approved connected-peer scope, but one connected expected peer remained incomplete after bounded scans; no production configuration or process mutation occurred
- Reopen 2 confirmed all connected peers complete, but one connected peer contained six conflict files; no production configuration or process mutation occurred
- Reopen 3 passed fresh preflight and applied the exact protected NAS-only candidate, but a newly connected seventh expected peer failed bounded convergence and disconnected
- Exact rollback restored the prior NAS configuration and converged the six remaining connected peers; no cache, process, Codex registry, LiteLLM registry, or peer configuration change occurred
- Reopen 4 passed candidate configuration and final-connected-set convergence, then failed the fresh official OpenCode package gate because plugin `0.2.0` raised a discovery-response type error
- Exact rollback again restored the prior NAS configuration and all six connected peers; no process was terminated and no selector/wire probe ran after the mandatory package failure
- Reopen 5 normalized exact-identity plugin caches to one healthy `0.2.1` tree on NAS and seven reachable peers, with integrity and fresh official initialization passing
- Reopen 5 rolled back the configuration candidate because its fresh protected backup initially inherited mode `0777`; mode was corrected and rollback completed before candidate propagation
- Reopen 6 completed descriptor-protected backup, exact NAS-only migration, stable connected-set convergence, healthy `0.2.1` fresh-process checks, and the full published-package contract matrix
- Active configuration now removes exactly 25 approved overrides, preserves five unrelated overrides/all unrelated settings, and retains exact unversioned plugin reference with mode `0600`
- Pre-existing long-running OpenCode sessions require user restart; offline/SSH-unreachable peers remain automatic convergence/cache follow-up
- Product and architecture documentation were already closed by the approved SCR/plan/plugin architecture contract; no additional steady-state document change is required

### Reopen 5 - 2026-08-27
- Corrective plugin `0.2.1` is published and verified against live NAS metadata.
- User explicitly requested punctual duplicate-cache cleanup and completion of the reasoning migration.
- Exact-identity cache inventory and protected cleanup completed on NAS plus seven reachable connected peers; unrelated caches were preserved.
- Fresh official OpenCode processes built exactly one `@latest` tree resolving spec/version `0.2.1` with matching npm integrity and successful model initialization on each reachable host.
- One connected expected peer was not SSH-reachable and remains package-cache follow-up; its shared configuration was not directly edited.
- The exact NAS configuration candidate passed structural checks, but its freshly created backup initially inherited mode `0777` instead of required `0600`.
- The backup mode was corrected and exact atomic rollback completed before candidate Syncthing propagation or functional matrix execution; healthy `0.2.1` caches were retained.
- Resume with a backup procedure that explicitly `fchmod(0600)`s the open descriptor and verifies mode before any configuration mutation.

### Reopen 6 - 2026-08-27
- Retained healthy canonical `0.2.1` caches already verified on NAS and seven reachable peers; no unrelated cache was touched.
- Fresh exact backup passed descriptor-level `fchmod(0600)`, owner, mode, size, checksum, and fsync gates before mutation.
- NAS-only atomic candidate removed exactly 25 approved overrides, preserved five unrelated overrides and every unrelated setting, retained exact unversioned plugin reference, zero file references, and mode `0600`.
- Seven peers in the final stable connected set converged at 100% with matching candidate checksum and zero conflicts; NAS remained idle/error-free.
- Eight reachable hosts passed fresh official model discovery with 36 models and one canonical installed `0.2.1` tree each.
- Published-package matrix passed nine families, 31 aliases, 164 explicit legacy/V2 bodies, defaults, user-last overrides, intrinsic default omission, retirement, and Spark preservation without production inference.
- No rollback was required; no user/control process was terminated.
