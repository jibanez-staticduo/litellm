# NAS functional residuals

> PMA independently accepted this final repair/deployment scope. The task is archived; [closure index and deferrals](../TASK-2026-09-05-003-close-dual-host-repair/SUMMARY.md) record acceptance without changing the runtime evidence below

## Current verified result, including Reopen 1

Both hosts are running/healthy on exact-source digest 0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c, application source 6ba4b3b366386e16364a6723c43319f4e52cc7a0. The active spend recursion is corrected, supported OAuth discovery restored, and all 951 isolated mapped tests pass with no skips. The unchanged Dockerfile built from the exact source archive. Fedora passed first; only then was the same digest promoted to NAS. Both pass renewed public Astra reload/Chat/Responses and aggregate partial-availability/healthy-tool checks, plus complete 900-second observations. Corrected startup wrappers remain intact

NAS had 148 RecursionError lines in five minutes before correction and zero since candidate startup through the complete observation and final reruns. Recent NAS spend records retain token and structured response fields. This is a scoped functional result, not an error-free all-traffic release claim: external Frigate reachability, other timeout/auth-required peers, ordinary client/provider limits and finite-window memory growth remain disclosed

## Root causes

Originally Astra's deployments retained mode=responses while the catalog lost chatgpt/gpt-6-astra. Chat missed its Responses bridge, hit the Codex chat/completions endpoint and received a browser challenge; cooldown produced later 429s. DB-only routers were missing from the live weak registry used for price-map metadata replay. Tracking initially empty routers restores metadata without changing profile fallback or provider limits

Optional MCP initialize probes lacked a whole-setup metadata deadline, and aggregate listings bounded only the inner list call rather than each peer's complete setup. AnyIO scopes now bound both paths, preserve classified peer failures and drain cancellation without suppressing healthy tools or changing scoped access/error semantics

The legacy host wrappers installed postgresql-client for an already-existing source_url column repair. Removing that obsolete dependency restored normal startup. Fedora's separate guarded Responses health correction was retained; NAS's simpler wrapper was reviewed independently. Both exec the image entrypoint. Original configuration is preserved in owner-only host backups, with secret-free final wrapper snapshots committed in config/

Reopen 1 proved active sanitizer recursion with deep dictionary/list chains and cyclic lists. Traversal now has a 32-level container bound and shared/cyclic container identity tracking. Normal spend fields and typed responses are preserved, arbitrary runtime objects are not rendered, and callbacks/input graphs are not mutated. Supported resource/issuer OAuth discovery now uses its restored existing guarded fetch helper rather than calling an absent method

## Acceptance criteria coverage

| Criterion | Status | Verification |
| --- | --- | --- |
| AC-1 | PASS for requested routing correction | Actual public Astra Chat and Responses JSON/stream pass after supported price reload on both hosts |
| AC-2 | PASS for bounded partial availability | Six deadline/cancellation/drain regressions; NAS exposes 487 tools from 24 successful peers with three truthful Frigate timeout outcomes |
| AC-3 | PASS with external limitation | Actual NAS Chat, initialize/list and real memory-health pass; fresh Frigate TCP probes still fail |
| AC-4 | PASS for requested sequence | Exact clean build, Fedora-first functional/900s pass, same-digest NAS promotion/900s pass, preserved configuration, final Fedora recheck |
| AC-5 | PASS | Numbered results, actual identities, config snapshots, checksums and resource samples; latest release in logs 09-11 |
| AC-6 | PASS | Local reproductions, 951 mapped tests, zero post-deploy recursion, 169 recent NAS spend rows including token/structured response fields, renewed functional/resource gates |

## Verification

Source verification totals 951 passing mapped tests in isolated Python processes, no skips. Direct production/spend-test Ruff, changed-file formatting, diff checks and StaticEng validation pass. Existing whole-manager-test lint findings and a combined-process command timeout remain disclosed in log 09, not presented as successful gates. Initial failing regressions and intermediate partial results remain in the chronological evidence

The formerly failing OAuth-discovery assertion is now fixed because inspection confirmed the missing helper affects a supported flow. All 475 manager tests, including its discovery guard class and the new advertised-resource flow, pass. No external OAuth credential or auth-required peer was changed

Both actual public endpoints pass fresh-nonce Astra Chat/Responses JSON and streams, supported catalog reload, standard aggregate initialize/list and a healthy real tool. NAS returns 24 ok/3 timeout peer outcomes; Fedora returns 11 ok/1 timeout/1 auth_required. End-to-end NAS listing takes 30-40 seconds because optional metadata setup can add ten seconds to the thirty-second peer listing boundary

Both renewed 900-second windows passed 31/31 readiness samples and zero memory-limit/OOM events. Memory.current increased by 205074432 bytes on Fedora and 114589696 bytes on NAS; this is not a plateau claim. Final health, same-container/digest identity and 8-GiB/no-swap/restart-disabled containment pass. See logs/10-reopen1-dual-host-pass.md and logs/11-reopen1-resource-samples.csv

## Documentation impact

Technical availability invariants and relevant CodeMaps are updated. No advertised product feature or UI behavior is added, so product overview and screenshots are not required

## Open risks and next step

PMA owns final acceptance/closure. Frigate requires its service/network owner; registrations were neither repaired nor hidden. Ordinary background rate-limit/client failures remain, but the active sanitizer recursion no longer appears in either candidate's complete post-startup logs. No clean-all-traffic or indefinite memory-stability claim is made. Retain ordinary memory monitoring and keep external provider/auth/network and deferred security work separate from the now-verified product corrections
