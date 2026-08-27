---
id: client-model-contracts-020-plan
scr: SCR-2026-08-26-002-client-model-contracts-020
status: completed
owner: product_manager
date: 2026-08-26
---

# Client Model Contracts Final Execution Record

## Final Outcome

The plan completed with corrective releases and approved scope changes. The deployed steady state is

- `@staticeng/opencode-litellm@0.2.2` through the exact unversioned shared reference
- Official OpenCode `1.18.23` with eight retained contract families and explicit official-default transmission
- Codex `0.149.1` with eight retained custom-catalog rows and exact Responses efforts
- Normal GPT-5.3 Codex and GPT-5.3 Codex Spark retired from both registries and both client catalogs, without redirects
- NAS `defend/gpt-5.5` route, dependencies, and override retired
- Explicit model and provider overrides applied last: user override over built-in contract over discovery
- No OpenCode core patch, Codex binary patch, LiteLLM source change, direct database write, or model-specific request validator

The approved SCR is the normative product contract. This document records how the completed work reached that state

## Final Architecture

### Internal Contract Catalog

The plugin owns one immutable typed catalog for exact retained aliases, ordered OpenCode modes, explicit official defaults, legacy/V2 bodies, and required reasoning metadata. It also owns the exact retired normal and Spark GPT-5.3 alias sets. Matching is exact and never fabricates an alias absent from discovery

Mode semantics are represented once and rendered per client

- GPT and native effort modes render legacy `reasoningEffort` and V2 `reasoning_effort`
- DeepSeek visible `off` renders wire `none`
- Qwen visible `off` renders only `chat_template_kwargs.enable_thinking=false`
- Official OpenCode's intrinsic default selector sends the explicit contract default
- `ultra` is never generated or sent

### Merge and Retirement Boundaries

The effective pipeline is discovery base, exact built-in contract, explicit model/provider overrides, then generic shape normalization. Explicit user overrides therefore win over built-in and discovered fields. Unknown-model behavior and established array/scalar replacement semantics remain unchanged

Both exact GPT-5.3 families are filtered from generated OpenCode catalogs even during stale-registry windows. Both registries remove their deployments and dependencies, and retired requests remain ordinarily unavailable without fallback or redirect

### Client Representation

Official OpenCode `1.18.23` receives all eight retained SCR rows. Codex `0.149.1` receives the same eight families with wire-valid subsets: DeepSeek `none/low/high/max`, Qwen `low/medium/xhigh`, and each GPT row's exact approved efforts. Codex stays on the Responses API and row switches may not leak stale effort values

## Completed Work Sequence

1. Task 015 implemented the initial contract catalog and exact merge/serialization behavior
2. Task 016 published and verified `0.2.0`
3. Task 017 migrated NAS-authoritative shared OpenCode configuration; corrective discovery-shape release `0.2.1` became the successful intermediate activation
4. Task 018 aligned the Codex catalog under authoritative Codex `0.149.1`; its nine-row Spark-preserving result was an intermediate snapshot
5. Task 019 retired obsolete routes Fedora-first and then NAS after the user expanded scope to retire Spark everywhere
6. Task 004 published and activated corrective plugin `0.2.2` and removed the Spark Codex row, producing the final eight-family/eight-row client state
7. Task 005 independently reran current OpenCode, Codex, and Fedora runtime gates
8. Task 020 reconciled the approved explicit-default decision and completed one final PASS trace across SCR AC-1 through AC-14

## Final Verification Gates

- Plugin `0.2.2`: clean build, 63/63 tests with zero skips, tracked-dist, package inventory, npm integrity, alias/near-match, retirement, and user-last override gates pass
- OpenCode `1.18.23`: eight retained representative rows, exact ordered named modes and explicit defaults, exact legacy/V2 wires, current deployed alias equivalence, no retired alias, and no stale/double plugin load pass
- Codex `0.149.1`: eight rows, all 40 exact Responses efforts, eight reverse-order row-switch no-leak captures, valid active DeepSeek `high`, and generated-cache non-mutation pass
- Fedora and NAS: normal and Spark GPT-5.3 deployments, fallbacks, and dependencies are absent; NAS defend is absent; unavailable-without-redirect and access-integrity gates pass
- Shared configuration: exact unversioned plugin reference, mode `0600`, no known/retired override, no `file://`, unrelated settings preserved, and connected-peer Syncthing convergence pass
- Evidence: redacted and free of credentials, prompts, response content, authorization material, deployment identities, database payloads, and unredacted configuration

## Historical Plan Decisions, Non-Normative

The following earlier plan statements are retained only to explain execution. They are superseded and must not be used to derive the deployed state

- **Release `0.2.0` and later `0.2.1`: superseded.** Both were valid milestones; the final published and activated package is `0.2.2`
- **Preserve Spark in catalog, clients, and registries: superseded.** Spark is retired everywhere. Former Spark request-health and preservation stop gates became absence, dependency cleanup, unavailable-without-redirect, access-integrity, and rollback gates
- **Codex `0.147`: superseded.** All authoritative catalog and wire validation uses installed Codex `0.149.1`
- **Nine contract families and nine Codex rows: superseded.** Removing Spark leaves eight retained families and eight Codex rows
- **Intrinsic-default omission: superseded.** Official OpenCode explicitly sends GPT-5.4/Mini `none`, GPT-5.5/5.6 `medium`, DeepSeek `max`, and Qwen `xhigh`
- **Stop on Spark HTTP 400 without mutation: historical intermediate stop.** The stop was correctly enforced, then investigation and user approval changed the target from preservation to retirement; Task 019 subsequently completed with PASS

## Rollback Boundaries

- Plugin rollback uses an explicitly authorized prior release and scoped exact-identity cache refresh; shared configuration remains unversioned unless the user approves a temporary pin
- OpenCode configuration rollback restores only a protected exact NAS backup atomically and lets NAS-authoritative Syncthing propagate it
- Codex rollback restores only the protected custom-catalog/config assets; generated cache is not hand-edited
- Registry rollback recreates exact protected route and dependency payloads through host-local authenticated APIs; database backups are last-resort recovery, not a direct-write mechanism

## Final Traceability

- SCR AC-1 through AC-6: Tasks 015, 004, 005, and 020
- SCR AC-7, AC-8, and AC-11: Tasks 017, 004, 005, and 020
- SCR AC-9: Tasks 019, 004, 005, and 020
- SCR AC-10 and AC-12: Tasks 018, 004, 005, and 020
- SCR AC-13: Tasks 015 through 020 plus corrective Tasks 004 and 005
- SCR AC-14: final Task 020 audit and linked redacted evidence packets

## Documentation Closure

The approved SCR is normative, this plan is a completed execution record, and Tasks 004/005/019/020 provide final-state evidence. Task 017 and Task 018 summaries are explicitly historical intermediate snapshots and point forward to those final artifacts
