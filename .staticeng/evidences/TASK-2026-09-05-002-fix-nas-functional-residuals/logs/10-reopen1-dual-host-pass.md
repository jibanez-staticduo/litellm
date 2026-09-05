# Reopen 1 dual-host source and runtime verification

## Exact source/build and deployment order

Source 6ba4b3b366386e16364a6723c43319f4e52cc7a0 was committed and non-force pushed before building. The unchanged repository Dockerfile built linux/amd64 from `git archive` of that full commit on Fedora; no dirty files entered the context. Schema, migrations, Dockerfile, dependency manifests and lock are unchanged from the preceding image. Build, Prisma generation and package installation completed successfully, with the inherited Wolfi/Prisma and Tornado cleanup warnings retained

Published tag: docker.staticduo.com/litellm:task0905-spend-6ba4b3b366

Published/shared OCI index: sha256:0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c

Linux/amd64 manifest: sha256:8f2b164c6b888789ac1ea0808247f59517812af3fa745662a5255e8e5736a467

Config: sha256:787db43ef92207e1b5557c55276833cfb095321b89c3e70f7c941e74fdc2d79e

Fedora was updated first, passed public functional checks, the installed-image sanitizer regression, a full 900-second observation, zero recursion markers and a post-soak public rerun. Only then was NAS updated to the same digest. NAS passed its public tests and 900-second observation, followed by final public tests on NAS and Fedora

Each deployment changed only LITELLM_IMAGE in that host's actual .env and recreated only LiteLLM through the existing docker-compose.yaml using --no-deps --pull never. Protected backups are under each host's existing Compose root at releases/TASK-2026-09-05-002-residuals-reopen1. Final byte comparisons prove all nonselector environment bytes, Compose, config.yaml and the corrected startup wrappers remain unchanged. No rollback, wrapper change, credential mutation, DB restore, Frigate change or unrelated tooling/security work occurred

## Final runtime identities and preservation

Fedora container: b820347e0bbfd3ddeb1e5b254359f3d47f5ab5235e21d9718ffcbbd1529f00f9

NAS container: 2b495d3851284ad9027d271d7adb3653156f027dcb9b71aeeddaacb413d33eda

Both selected references equal docker.staticduo.com/litellm@sha256:0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c. Image revision is 6ba4b3b366386e16364a6723c43319f4e52cc7a0. NAS reports the config as its engine image ID; Fedora reports the OCI index. These are the same release, not compared as identical engine representations

Final state on both: running/healthy, restart count 0, OOMKilled=false, memory=8589934592, memory+swap=8589934592, restart=no. Cgroup swap.max=0. NAS retains 38 model deployments and 27 MCP registrations with the same alias/server-ID digests recorded before promotion. The existing source_url column remains present

Both host wrapper checksums still match the committed snapshots: Fedora 4f62fbc87dc6a304bae910482b49c2f0aa33de0317f88e622ae5d15000176cc0; NAS 15a1d5207f5a36b5961ba922532fc5fbbe9584d70480e746f53fcf0b2ca4935c. Fedora's inherited health override remains host-specific; no byte-identical overridden runtime-files claim is made

## Recursion eliminated under the active workload

Before correction: 148 RecursionError lines in a fresh five-minute NAS window, with sanitized frames repeatedly pointing to the spend sanitizer's dictionary/list traversal. Local deep dictionary/list chains and a self-referencing list failed before and passed after correction

Both installed images pass the same synthetic 2000-level dictionary, cyclic-list and callback-nonmutation check without connecting to a provider or traversing private runtime objects. Normal usage fields remain present and the result is JSON serializable

After NAS's full observation, the complete log stream since candidate startup contained zero RecursionError markers. The final collection after both public reruns again contained zero, across 47892 NAS lines and 87147 Fedora lines. The collection did not retain raw log lines. Both also had zero MemoryError, P3009, P3018, migration-failed, no-deployments-available and unsupported-health-patch markers

A read-only aggregate query over NAS spend records from the most recent ten minutes, entirely after candidate startup, returned 169 rows, 28 rows with positive token counts and 24 rows with structured choices/output response fields. Earlier post-soak sampling returned 157/22 rows/token rows. These establish that the formerly failing live spend path is producing records and preserving structured spend/response fields, not merely suppressing the traceback

A separate Fedora recent-spend query returned zero rows. No Fedora DB persistence claim is made from that query; Fedora's installed sanitizer, full source tests, actual calls and zero-recursion observations passed. No logging configuration was altered to manufacture records

The supported OAuth discovery repair is covered by the new advertised-resource challenge regression and the complete 475-test manager file, including the formerly failing metadata guard cases. Live external auth-required outcomes remain visible; no OAuth grant, credential repair or all-account authentication success is claimed

## Final public functional requests

Fresh-nonce prompts bypassed reuse of the prior synthetic response cache. Existing administrator credentials remained only in each host process's memory. Model response text had to equal OK; streaming additionally required stop/response.completed. Tool output bodies and private payloads were not retained

| Final gate | NAS public URL | Fedora public URL |
| --- | --- | --- |
| Readiness | 200, 0.029s | 200, 0.017s |
| Supported price-map reload | 200, 0.179s | 200, 0.108s |
| Astra mode after reload | responses | responses |
| Astra Chat JSON | 200, 3.521s | 200, 2.925s |
| Astra Chat stream | 200, 2.386s | 200, 1.783s |
| Astra Responses JSON | 200, 5.976s | 200, 3.051s |
| Astra Responses stream | 200, 3.855s | 200, 2.796s |
| Unscoped /mcp initialize | 200/result, 10.052s | 200/result, 1.038s |
| Unscoped /mcp tools/list | 487 tools, 30.223s | 147 tools, 30.039s |
| Peer outcomes | 24 ok, 3 timeout | 11 ok, 1 auth_required, 1 timeout |
| Healthy real tool | memory-health, no RPC error/isError, 10.172s | memory_whoami, no RPC error/isError, 1.061s |

Public URLs are https://litellm.staticduo.com and https://litellm.defend.tech respectively. Frigate registrations still report timeout. Fresh TCP attempts to their unchanged registered endpoints remain unsuccessful: 3.005s admin, 7.009s observe, 3.003s breakglass, including name resolution. These are external reachability limitations, not hidden successful peers

## Bounded resource observation

| Measurement | Fedora | NAS |
| --- | ---: | ---: |
| Duration | 900.00s | 900.00s |
| Readiness samples | 31/31 pass | 31/31 pass |
| memory.current start | 966545408 | 1044283392 |
| memory.current end/peak | 1171619840 | 1158873088 |
| Delta | +205074432 | +114589696 |
| Anon start | 896184320 | 955686912 |
| Anon end | 1097076736 | 1068847104 |
| max/oom/oom_kill events | 0 throughout | 0 throughout |

Same container identity and 8-GiB/no-swap containment held through each thirty-second-cadence observation. No forced GC, cache clearing or operator model/MCP load was used during the windows; background clients remained active. These are finite bounded-resource passes, not proof of a plateau or indefinite leak freedom. Samples are retained in logs/11-reopen1-resource-samples.csv

Final health after both public reruns: readiness and liveliness 200 on each host, NAS memory.current=1179455488 and Fedora=1304604672, all recorded memory event counters zero

## Remaining limitations

Ordinary client/provider limit errors and unavailable peers remain visible. Final NAS log counts include 269 HTTP 429 and 6 HTTP 400; Fedora includes 804 HTTP 429 and 91 HTTP 404. RouterRateLimitError, masked upstream status failures and classified MCP cancellation/list faults explain the retained exception-type categories. No rate-limit policy was bypassed and no clean-all-traffic/all-provider claim is made

No new security scan, signing review, credential rotation, external Frigate repair or maintenance-tool repair is claimed. Existing whole-manager-test lint findings and the combined-process timeout remain disclosed in log 09; the complete isolated mapped source tests total 951 passed, no skips

## Acceptance criteria

AC-1 through AC-5: renewed PASS for the requested source/build, exact Fedora-first/NAS deployment, Astra reload/Chat/Responses, bounded MCP partial availability, preservation and evidence contracts, with external limitations above

AC-6: PASS. Active recursion reproduced locally and in sanitized live frames, minimal bounded sanitizer shipped, typed/normal spend fields and callbacks covered, zero post-deploy recursion on both hosts, actual NAS spend records with structured response fields, public functional reruns and complete resource windows verified. PMA retains final closure

Final evidence validation: git diff --check passes and staticeng_validate passes with zero warnings. No application-source or tracked task/evidence changes are planned after the final closure-evidence commit; subsequent PMA acceptance remains separate
