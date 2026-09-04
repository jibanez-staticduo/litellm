# TASK-2026-09-03-020 Evidence Summary

## Summary

PASS. The approved SCR now freezes exact official `linux/amd64` PostgreSQL 16.15 and Redis 7.4.11 manifest/config identities and authorizes exactly one replacement TASK-018 disposable lifecycle only after implementation and Tech Lead source/test approval. No runtime mutation occurred

## Work Performed

Read-only official Docker Hub registry resolution on 2026-09-04 established these frozen subjects:

```text
postgres:16-alpine index sha256:cf78e76683b9ca8c5733cbbdce6c9262b45b6767934dd0a95e671f9a0fc20685
postgres linux/amd64 manifest sha256:075f7ba66bc9b3ce7d6b8b635208ff61cd7cf1a67d71ec530eec5d7ae0cbe571
postgres OCI config sha256:75f5a96988cdf694a215073c3e9c001b706b371e2f94df3967f2efdec2787f6b
postgres version 16.15
redis:7-alpine index sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf
redis linux/amd64 manifest sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c
redis OCI config sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb
redis version 7.4.11
```

The SCR requires the selected daemon to pull each exact child digest once with explicit `linux/amd64`, then inspect exact repository digest, config/image ID, OS, and architecture before creating any task resource. It also requires source-level missing-image and partial-create regression coverage and automatic ownership-checked zero-resource cleanup on every failure. Cached images may remain and must not be removed

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact child manifests, OCI configs, `linux/amd64` platform, and dependency versions are frozen; tags and indexes are provenance only
- **AC-2: PASS.** Pull and local identity verification for both immutable references precede every network, volume, and container creation
- **AC-3: PASS.** Image cache retention is allowed, but every ownership-proven task resource must clean automatically on every failure and pass name, ID, and complete-label absence checks
- **AC-4: PASS.** Exactly one replacement TASK-018 lifecycle is authorized after Developer implementation and Tech Lead source/test PASS; the first authorization remains consumed
- **AC-5: PASS.** All TASK-019 isolation, synthetic state, internal networking, loopback exposure, active cancellation, NAS production invariants, no-deploy, and Fedora/NAS production restrictions remain mandatory

## Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md`, completed TASK-020, and updated current/done task registries. No product, feature, architecture, technical, or CodeMap update is required because steady-state product behavior did not change

## Open Risks

TASK-018 source does not yet implement the frozen references, pre-resource pull/identity gates, or missing-image zero-resource regression. No pull or replacement lifecycle may occur before those changes pass Tech Lead review. Pull/preflight failure requires a stop and PMA return without retry; automatic cleanup residue blocks all progression

## Recommended Next Step

PMA should route TASK-018 Reopen 9 to Developer, then Tech Lead source/test review. Only a PASS may unlock the one replacement disposable lifecycle. TASK-006 and Fedora remain blocked

## Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-020 PASS. Exact PostgreSQL 16.15 and Redis 7.4.11 `linux/amd64` manifest/config identities are frozen in the approved SCR. One replacement TASK-018 lifecycle is authorized only after source implements immutable refs, pre-resource exact-platform pull and identity verification, and automatic zero-resource cleanup regressions, then receives Tech Lead PASS. Cached images may remain. Every TASK-019 isolation, NAS production invariant, no-deploy, and Fedora boundary remains mandatory. No runtime mutation occurred
