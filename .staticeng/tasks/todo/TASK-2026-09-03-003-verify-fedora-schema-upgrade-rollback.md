---
id: TASK-2026-09-03-003-verify-fedora-schema-upgrade-rollback
complexity: complex
track: implementation
slice: qa
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: Verify Fedora schema upgrade and rollback

## Objective

Prove the qualified candidate can upgrade an isolated representation of Fedora's current database schema and that the current rollback image can start safely against the upgraded schema, without changing Fedora production data or services.

## Acceptance Criteria

- [ ] AC-1: Capture a secret-free schema/migration-state representation from Fedora through read-only commands, with no application rows or credential values.
- [ ] AC-2: Restore it into a uniquely labelled disposable PostgreSQL instance isolated from production.
- [ ] AC-3: Exact candidate final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` applies all ten pending migrations and starts healthy with schema state current.
- [ ] AC-4: Exact current Fedora rollback image starts healthy against a clone of the upgraded schema without destructive or reverse migrations.
- [ ] AC-5: Migration before/after state, idempotent candidate restart, rollback-image compatibility, logs, and checksums are evidenced without secrets.
- [ ] AC-6: Destroy every disposable container/network/volume/worktree/schema artifact after evidence capture and prove Fedora production remains unchanged.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Use read-only, allowlisted Fedora commands and never export application table data, encrypted values, credentials, URLs, keys, or environment. Prefer `pg_dump --schema-only` plus only the minimum migration-ledger rows required to reproduce current migration state; review/sanitize the artifact before transfer and never store its contents in repository evidence. Run the disposable PostgreSQL/candidate/rollback compatibility stack on the currently authorized standalone Docker daemon with unique labels and no production mounts/networks. Use the exact candidate and exact current Fedora image identities. Destroy all disposable runtime resources and the schema artifact before handoff. Do not deploy, restart Fedora, alter Fedora DB/config, publish/sign images, or touch NAS production.

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

- AC-1: PASS. Read-only Fedora capture contained schema-only DDL and the minimum 151-row migration ledger, with zero application data statements or credential URL markers; the owner-only temporary fixture was not retained
- AC-2: PASS. The fixture restored into uniquely task-labelled PostgreSQL 17 container, network, and volume resources with no host ports, production mounts, or production networks
- AC-3: PASS. Exact candidate `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` applied the exact ten pending migrations, reached healthy at 161 successful migrations, and completed two idempotent healthy restarts
- AC-4: PASS. Exact current Fedora rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` reached healthy against the upgraded clone with no schema or ledger change
- AC-5: PASS. Evidence records identities, checksums, state counts, health, restart behavior, and secret-safe log classifications only; raw fixture and logs were destroyed
- AC-6: PASS. Task-labelled containers, network, volume, source/split fixture, raw logs, and temporary runtime/schema artifacts are absent; Fedora identity, health, start time, restart/OOM state, normalized schema, and migration ledger are unchanged
- Product, architecture, technical, and CodeMap documentation are not required because QA changed no product behavior or maintained source/test structure
- Evidence: `.staticeng/evidences/TASK-2026-09-03-003-verify-fedora-schema-upgrade-rollback/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

PASS. Exact candidate `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` upgraded a secret-free Fedora schema/ledger clone from 151 to 161 successful migrations, reached healthy, and restarted idempotently. Exact Fedora rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` reached healthy against the upgraded clone without schema or ledger change. All disposable resources and artifacts were destroyed, and Fedora remained unchanged. This clears only the isolated migration blocker; publication, signing, deployment, backup, and soak remain unauthorized
