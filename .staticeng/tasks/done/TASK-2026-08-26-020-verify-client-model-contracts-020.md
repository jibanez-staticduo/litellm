---
id: TASK-2026-08-26-020-verify-client-model-contracts-020
complexity: complex
track: investigation
slice: qa
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 2
---

# Task: TASK-2026-08-26-020 - Verify Client Model Contracts 0.2

## Objective
Independently verify the completed plugin, OpenCode, Codex, Syncthing, and dual-registry steady state before SCR closure.

## Acceptance Criteria
- [x] T6-AC-1: Rerun plugin catalog integrity, aliases/near-matches, override precedence, build/tests/pack, npm latest/integrity, installed versions.
- [x] T6-AC-2: Fresh official OpenCode on synchronized reachable hosts exposes approved GPT/DeepSeek/Qwen matrix/payloads, no retired aliases or stale plugin errors.
- [x] T6-AC-3: Fresh Codex 0.149.1 exposes approved wire-valid rows/modes/Responses efforts, active config preserved, generated cache not hand-edited.
- [x] T6-AC-4: Both LiteLLM registries persistently lack normal GPT-5.3 and Spark; NAS also lacks defend; dependencies absent; no redirects.
- [x] T6-AC-5: NAS source config, connected Syncthing peers, permissions/hashes/unrelated paths remain converged; offline peers documented.
- [x] T6-AC-6: Trace SCR AC-1 through AC-14 across evidence; discrepancies reopen original tasks.
- [x] T6-AC-7: Final report records versions/checksums/releases/residual risks without secrets/prompts/responses.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-020-verify-client-model-contracts-020/` with `SUMMARY.md` and redacted logs.

## Constraints
Read-only QA. No route/config/cache/process mutation.

## Reopen History

### Reopen 1 - 2026-08-27
- Initial QA rejected closure solely because independent fresh OpenCode/Codex/Fedora runtime matrices were missing.
- Task 005 produced fresh independent PASS evidence for the complete OpenCode 0.2.2 matrix, Codex 0.149.1 eight-row wire matrix, and Fedora API/raw/no-redirect gates.
- Resume final evidence trace and closure decision without new mutations.

### Reopen 2 - 2026-08-27
- Final QA found runtime explicit-default behavior contradicted older SCR omission wording.
- User approved explicit official-default transmission. SCR and execution plan were reconciled without code/runtime changes.
- Resume documentation-only AC trace and closure decision.

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

- Closure decision: REJECT
- Plugin `0.2.2` independently passes build, 63/63 tests with zero skips, tracked-dist, 19-file pack, npm latest/integrity, exact alias/near-match, retirement, and override-precedence gates
- Fresh OpenCode `1.18.23` NAS/Fedora discovery, matching shared-config hashes/mode, one `0.2.2` cache tree, retained family counts, and GPT-5.3 absence pass
- Current Codex `0.149.1` eight-row catalog/config/cache invariants and current NAS LiteLLM API/raw absence pass
- Six reachable Syncthing instances are idle, complete, need nothing, and report no errors; ProArt, UT2, Mac, and CachyOS return HTTP 502 and remain documented offline/unreachable
- Required independent fresh full OpenCode selector/wire matrix, Codex eight-row wire matrix, and current Fedora API/raw/no-redirect gates remain unverified; prior implementation evidence is insufficient for independent QA closure
- Complete redacted evidence is in `.staticeng/evidences/TASK-2026-08-26-020-verify-client-model-contracts-020/`
- Product documentation is not required; this investigation changes no steady-state product behavior or source structure

## QA Engineer: Reopen 1 Post Implementation Expectations

- Closure decision: REJECT on one governing-contract discrepancy; no implementation/runtime matrix gap remains
- Task 005 is independent, read-only, redacted, and complete: OpenCode `1.18.23` plus plugin `0.2.2` passed 41 named modes and eight no-variant captures on each of NAS/Fedora safe metadata shapes, 21 deployed aliases, and zero stale/load/double-load errors
- Codex `0.149.1` passed all eight rows, 40 Responses mode captures, eight reverse-order no-leak switches, valid active DeepSeek `high`, and production config/catalog/cache non-mutation
- Fedora passed five current read APIs, eight zero-valued read-only raw/dependency aggregates, unchanged access fingerprint, and eight unavailable/no-deployment/no-redirect retired-alias probes
- Current NAS registry/config and six reachable Syncthing instances remain healthy, converged, and target-free; ProArt, UT2, Mac, and CachyOS remain HTTP-502 unreachable follow-up
- Blocker: Task 005's no-variant captures send explicit contract defaults, while approved SCR AC-7 requires intrinsic Default to omit model-specific reasoning controls
- Product documentation clarification is required through the approved SCR process if explicit contract-default transmission is intended; otherwise reopen the originating implementation scope
- Reopen 1 audit is recorded in `.staticeng/evidences/TASK-2026-08-26-020-verify-client-model-contracts-020/SUMMARY.md` and `logs/05-reopen1-independent-evidence-audit.log`

## QA Engineer: Reopen 2 Post Implementation Expectations

- Closure decision: APPROVE; no blocking finding remains under the user-approved explicit official-default semantics
- SCR AC-1 through AC-14 and T6-AC-1 through T6-AC-7 all pass using existing fresh evidence; no runtime rerun or mutation occurred
- Corrected final Task 005 OpenCode count is 41 named modes plus eight explicit-default captures per NAS/Fedora source, 49 per source and 98 total
- Codex `0.149.1` remains fully covered by eight rows, 40 exact Responses mode captures, and eight reverse-order no-leak switches
- Fedora and NAS registry absence/dependency/no-redirect gates, NAS config/client invariants, and the approved reachable Syncthing scope all pass
- Offline peers, npm OIDC authorization, and the unrelated repository-wide CodeMap backlog remain documented non-blocking follow-ups
- Documentation closure is complete in the reconciled SCR/plan and final evidence; no implementation task needs reopening
- PMA owns final task/SCR closure and may proceed to architecture and Tech Lead review
