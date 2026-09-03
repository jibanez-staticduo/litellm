# TASK-2026-09-03-003 Evidence Summary

## Summary

PASS. A read-only, secret-free Fedora schema and migration-ledger fixture was restored to a uniquely labelled disposable PostgreSQL 17 instance. Exact candidate config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` applied the exact ten pending migrations, reached healthy, and restarted idempotently. Exact current Fedora rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` then reached healthy against the upgraded schema without changing schema or ledger state. All disposable runtime and schema artifacts were destroyed, and Fedora remained unchanged

## Work Performed

- Captured Fedora with read-only `pg_dump --schema-only --no-owner --no-acl` plus only `_prisma_migrations` ledger columns; no application rows, credential values, environment, configuration, or URLs were captured
- Reviewed the temporary owner-only fixture before use: 73 schema tables, zero `COPY` statements, zero `INSERT` statements, 151 successful distinct ledger rows, zero failed or rolled-back rows, and zero credential URL markers
- Restored the fixture into PostgreSQL image `sha256:d741b376874687de90374fd34f55c6b2760e8f7bd7e4ae5cd47f50757fc08cf8` on unique task-labelled container, network, and volume resources with no host ports, production mounts, or production networks
- Compared packaged migration sets: candidate has 161, rollback has 151, and their exact ten-name difference has SHA-256 `81fdcd2be453adffadf09429c4782a446612a806328fbe6cea05dfe6ed40eb4c`
- Started the exact candidate, observed all ten migrations applied and schema state at 161 successful distinct rows, then completed two healthy idempotent restarts with unchanged normalized schema and ledger checksums
- Started the exact rollback image against the upgraded clone, observed healthy status with restart 0 and OOM false, and proved normalized schema plus migration ledger checksums were unchanged
- Classified sanitized logs by counts and checksums only: no traceback, migration failure, HTTP 500, or unknown-migration warning occurred; candidate logged ten migration applications and successful post-migration completion; restarts and rollback logged no pending migrations
- Destroyed the disposable candidate, rollback, database, network, volume, split fixture files, source fixture, raw logs, and temporary checksum inputs; post-cleanup task-labelled container/network/volume and owned runtime-artifact counts are all zero
- Re-ran the Fedora read-only baseline after cleanup; container identity/start time, exact selector, running/healthy state, restart 0, OOM false, and the 151-row migration ledger checksum match preflight
- Ran `staticeng_validate`; result PASS with zero warnings

## Acceptance Criteria Coverage

- **AC-1: PASS, integration/manual.** Read-only Fedora extraction produced schema-only DDL plus the minimum migration ledger. Inspection proved no application data statements or credential URL markers. The temporary artifact was mode `0600` and was never stored in evidence
- **AC-2: PASS, integration.** The fixture restored into isolated, uniquely task-labelled PostgreSQL resources with no published port or production attachment. Restored state was 151 successful, distinct migrations and zero failures, rollbacks, or stored logs
- **AC-3: PASS, integration/E2E.** Exact candidate config applied the exact ten pending migrations, reached healthy, and produced 161 successful distinct migrations with no pending, failed, rolled-back, or logged-error rows
- **AC-4: PASS, integration/E2E.** Exact current Fedora rollback config reached healthy against the 161-migration upgraded clone. It reported no pending migrations and changed neither normalized schema nor migration-ledger checksum
- **AC-5: PASS, integration/manual.** Evidence records exact image/config identities, migration-set and state checksums, health, idempotent restart results, rollback compatibility, and secret-safe log classifications without retaining raw runtime logs
- **AC-6: PASS, integration/manual.** All disposable runtime/schema artifacts were destroyed. Fedora's exact LiteLLM identity and start time remained unchanged, and its migration ledger remained `151|0|0|151|151|0` with SHA-256 `dbe062506165bb0babb7ad3f3e2ae59769bd7aef194ce38c57c07d12e5f67c11`

## Verification Subjects And Checksums

```text
candidate config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
rollback registry selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
PostgreSQL config: sha256:d741b376874687de90374fd34f55c6b2760e8f7bd7e4ae5cd47f50757fc08cf8
candidate migration-set SHA-256: bd39ff9ecca85da8b82685f00532c6c22e87b8907003917e4074f1544fe9273f
rollback migration-set SHA-256: eba7f17da315150f9cd4d3dcd57c8beca4d85ae32af69f8513206141aa48bbfb
exact pending-set SHA-256: 81fdcd2be453adffadf09429c4782a446612a806328fbe6cea05dfe6ed40eb4c
upgraded normalized schema SHA-256: 0caa0590706e5a4f94c0b4152166db3f04ae4d282c689de9a7de7be5b54f6be9
upgraded migration-ledger SHA-256: 3acc73bbecec0c70978a1a05fce5352a40317fb035d6cddaaf8a313aeff10fa2
Fedora migration-ledger SHA-256 pre/post: dbe062506165bb0babb7ad3f3e2ae59769bd7aef194ce38c57c07d12e5f67c11
```

## Documentation Impact

Product, architecture, technical, and CodeMap documentation are not required because QA changed no product behavior, source structure, routes, schema, migration, or maintained test tooling

## Open Risks

- This fixture intentionally contains no application rows. It proves schema and ledger compatibility, including zero-row execution paths for the two bounded data-update migrations, but does not exercise those updates against populated production-like rows
- This task clears only the isolated current-schema upgrade and prior-image startup blocker. Signing, attestations, immutable registry publication, fresh deployment-time backup/restore, production smoke gates, and the 15-minute Fedora observation remain separately required
- The rollback image accepts ten applied migrations unknown to its packaged set because its startup path treats them as no pending work. Future application requests against newly changed tables remain outside this startup-only rollback criterion

## Recommended Next Step

PMA should accept this signed QA pass for the migration blocker, keep Fedora deployment blocked on the separate signer/publication and release-readiness gates, and route the result back to Tech Lead reauthorization

## Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

PASS. Exact candidate `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` upgraded a secret-free Fedora schema/ledger clone from 151 to 161 successful migrations, reached healthy, and restarted idempotently. Exact Fedora rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` reached healthy against the upgraded clone without schema or ledger change. All disposable resources and artifacts were destroyed, and Fedora identity, health, start time, restart/OOM state, and migration ledger remained unchanged. This clears only the isolated schema upgrade/rollback-startup blocker; publication, signing, deployment, backup, and soak remain unauthorized
