# Reopen 1 Authorization Verification

## Exact Registry Subjects

```text
builder manifest: sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa
builder config: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
builder platform: linux/amd64
builder source: bf58974a935521fa570fa7e280c51a00b2e5b54e
builder config equality: PASS
final manifest: sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
final config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
final platform: linux/amd64
final source: bf58974a935521fa570fa7e280c51a00b2e5b54e
final config equality: PASS
unique builder tag still resolves to exact builder manifest: PASS
unique final tag still resolves to exact final manifest: PASS
```

## Fresh Signature And Attestation Verification

The retained release public key has file SHA-256 `3983a067c0f99ec9e44e91b58f0991e6a065c74a11c6e70095abe178904005ec` and SPKI SHA-256 `2b3b91453b283be502c0cd035d835d5b58faa42b1f638297c45da75b09a15e71`. All six predicate files pass their retained SHA-256 manifest. Builder/final SPDX and CycloneDX predicates are byte-identical to TASK-011 Reopen 6 qualification artifacts

Cosign 3.1.3 was downloaded from the exact release URL into a disposable `/tmp/opencode` path and checked against SHA-256 `4629c757b7618056f8ddd7e2625ae9fdd94c0372a65049520bc7d9df9efc7f71`. Fresh verification passed for each digest:

```text
image signature with exact task/revision annotations: PASS
SPDX attestation: PASS
CycloneDX attestation: PASS
SLSA provenance v1 attestation: PASS
Cosign claims: PASS
public-key cryptography: PASS
transparency-log inclusion: PASS
```

The disposable Cosign binary and directory were removed after verification. No signing secret, private path, password, registry token, or decoded payload was retained

## Schema And Rollback Prerequisite

TASK-003 evidence was reviewed against exact candidate config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`:

```text
Fedora fixture start state: 151 successful migrations
candidate pending set: 10
candidate upgraded state: 161 successful migrations
candidate healthy starts: initial plus 2 idempotent restarts
rollback image healthy against upgraded state: PASS
schema/ledger mutation by rollback image: none
task disposable resources/artifacts after cleanup: 0
Fedora production identity/ledger change: none
```

The fixture contains no application rows. Fresh production backup and isolated restore verification therefore remain mandatory in TASK-012 before selector mutation

## Main And Fedora Baseline

```text
main: 761742b1c98e68502e7b638bb61d8a0a5e93c4bc
origin/main: 761742b1c98e68502e7b638bb61d8a0a5e93c4bc
qualified source ancestor: PASS
frozen upstream ancestor: PASS
non-StaticEng changes after qualified source: 0
Fedora selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
Fedora config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
Fedora source: 64a3b83bf0bdd8813890d20ba7b6b57fc034bb95
Fedora state: running, healthy, restart 0, OOM false
readiness/liveliness: 200/200
model rows: 26
model projection SHA-256: 98f0d541823b9f7c19c0a19d338e2f9027b07b6801015d2aeb5ab739229e6231
fallback rules: 24
fallback projection SHA-256: a057787927e9cfb8f5b140f7b4ed7e7f90f792e88fdc86b84d0ffdb7cf2c0f0c
qualified default/account2 aliases: 6/6
MCP registrations: 13
MCP status: 11 healthy, 1 auth-required, 1 unknown
exact release image already pulled on Fedora: no
```

PostgreSQL, Redis, admin MCP, and compat admin MCP dependency identities/start times remain unchanged and healthy. Compose, config, and wrapper hashes match prior review. The `.env` contains exactly one immutable image selector and remains mode 0600. No current DB dump exists, as expected before TASK-012's authorized fresh backup preflight

## Safety And Verdict

No image push/pull/sign/tag operation, registry mutation, Fedora/NAS file or DB mutation, container restart/recreation, deployment, or stable-tag movement occurred in this review

Verdict: AUTHORIZE TASK-012 under the exact preflight, backup/restore, Fedora-only deploy, full behavior, 900-second soak, and rollback contract recorded in the task
