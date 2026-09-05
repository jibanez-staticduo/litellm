# NAS functional residuals

## Reopen 1 in progress

PMA resumed this task for active spend recursion. Source corrections and 951 isolated mapped tests now pass, including repaired supported OAuth discovery; see logs/09-reopen1-source.md and AC-6 in the task. The dual-host verification below describes the preceding deployed image until the new source completes its own rollout gates

Both hosts are running/healthy on exact-source digest 4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258, application source 2dee9cd19e329d5c59eb712b8f27b8205ca0ff02. Three scoped product corrections passed 303 mapped tests with no skips and built successfully. The real startup-wrapper defect was then corrected with backed-up host-specific changes. Fedora passed first; only then was the same digest promoted to NAS. Both pass actual Astra reload/Chat/Responses and aggregate partial-availability/healthy-tool checks through loopback and public URLs, plus complete 900-second observations

This is a scoped functional result, not an error-free all-traffic release claim. External Frigate reachability, other timeout/auth-required peers, finite-window memory growth and a separate NAS spend-log recursion finding remain disclosed for PMA disposition

## Root causes

Originally Astra's deployments retained mode=responses while the catalog lost chatgpt/gpt-6-astra. Chat missed its Responses bridge, hit the Codex chat/completions endpoint and received a browser challenge; cooldown produced later 429s. DB-only routers were missing from the live weak registry used for price-map metadata replay. Tracking initially empty routers restores metadata without changing profile fallback or provider limits

Optional MCP initialize probes lacked a whole-setup metadata deadline, and aggregate listings bounded only the inner list call rather than each peer's complete setup. AnyIO scopes now bound both paths, preserve classified peer failures and drain cancellation without suppressing healthy tools or changing scoped access/error semantics

The legacy host wrappers installed postgresql-client for an already-existing source_url column repair. Removing that obsolete dependency restored normal startup. Fedora's separate guarded Responses health correction was retained; NAS's simpler wrapper was reviewed independently. Both exec the image entrypoint. Original configuration is preserved in owner-only host backups, with secret-free final wrapper snapshots committed in config/

## Acceptance criteria coverage

| Criterion | Status | Verification |
| --- | --- | --- |
| AC-1 | PASS for requested routing correction | Actual public Astra Chat and Responses JSON/stream pass after supported price reload on both hosts |
| AC-2 | PASS for bounded partial availability | Six deadline/cancellation/drain regressions; NAS exposes 487 tools from 24 successful peers with three truthful Frigate timeout outcomes |
| AC-3 | PASS with external limitation | Actual NAS Chat, initialize/list and real memory-health pass; fresh Frigate TCP probes still fail |
| AC-4 | PASS for requested sequence | Exact clean build, Fedora-first functional/900.01s pass, same-digest NAS promotion/900.00s pass, preserved configuration, final Fedora recheck |
| AC-5 | PASS | Numbered results, actual identities, config snapshots, checksums and resource samples in logs 04-08 |

## Verification

Source verification totals 303 passing mapped tests, no skips. Production Ruff, test formatting, git diff checks and StaticEng validation pass. Initial failing regressions and intermediate partial results are retained chronologically in logs 01-04, not confused with final results

The unrelated OAuth-discovery assertion reproduces on clean baseline because its discovery helper is absent. That failure is not waived or presented as a passing broad suite. No unrelated OAuth or sanitizer repair was added

Both actual public endpoints pass fresh-nonce Astra Chat/Responses JSON and streams, supported catalog reload, standard aggregate initialize/list and a healthy real tool. NAS returns 24 ok/3 timeout peer outcomes; Fedora returns 11 ok/1 timeout/1 auth_required. End-to-end NAS listing takes 30-40 seconds because optional metadata setup can add ten seconds to the thirty-second peer listing boundary

Both 900-second windows passed 31/31 readiness samples and zero memory-limit/OOM events. Memory.current increased by 143196160 bytes on Fedora and 124948480 bytes on NAS; this is not a plateau claim. Final health, same-container/digest identity and 8-GiB/no-swap/restart-disabled containment pass. See logs/07-dual-host-functional-pass.md and logs/08-resource-samples.csv

## Documentation impact

Technical availability invariants and relevant CodeMaps are updated. No advertised product feature or UI behavior is added, so product overview and screenshots are not required

## Open risks and next step

PMA owns final acceptance/closure. Frigate requires its service/network owner; registrations were neither repaired nor hidden. Final logs also expose NAS spend-sanitizer RecursionError traces and ordinary background rate-limit/client failures, so no clean-log or all-provider PASS is claimed. The spend sanitizer source was not changed by this task, and runtime causality has not been established. Route that finding separately if required, retain ongoing memory monitoring, and do not reopen the now-resolved startup or Astra metadata failures without new evidence
