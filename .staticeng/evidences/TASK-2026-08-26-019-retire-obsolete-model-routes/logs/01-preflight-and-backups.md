# Preflight And Backup Evidence

## Health And Backups

| Host | Readiness | DB | Dump format | Dump bytes | SHA-256 | Restore listing |
| --- | --- | --- | --- | ---: | --- | ---: |
| Fedora | HTTP 200 | connected | PostgreSQL custom | 75,017,755 | `b490df967c9e49224372e021ea79c02848496f6c4af8126966215978c376f7e4` | 417 entries |
| NAS | HTTP 200 | connected | PostgreSQL custom | 692,998,144 | `e793539ba3023feaf6e7bb5ea7e60833706d62666d8ff064114f5b4e29df2422` | 415 entries |

Both `sha256sum -c` checks passed. Both `pg_restore --list` commands succeeded. Dumps, listings, checksums, raw rows, API snapshots, and exact recreation payloads are mode `0600` in mode `0700` host-local task directories

## Fresh Fedora Targets

| Deployment | Exact ID | Upstream | Access | State |
| --- | --- | --- | --- | --- |
| `chatgpt/gpt-5.3-codex` | `b175303a-eb59-43e4-ad65-22c42a98c649` | `chatgpt/gpt-5.3-codex` | direct; one team | unblocked |
| `chatgpt-account2/gpt-5.3-codex` | `51d9260e-ac4d-4294-ab95-930afdb5a012` | `chatgpt/gpt-5.3-codex`, account2 profile | direct; one team | unblocked |

Fresh Fedora routing has two general fallback dependencies that must be removed before deleting deployments:

```text
chatgpt/gpt-5.3-codex -> chatgpt-account2/gpt-5.3-codex
chatgpt-account2/gpt-5.3-codex -> chatgpt/gpt-5.3-codex
```

Fedora has no Spark deployment or group, so no Fedora Spark request applies

## Fresh NAS Targets

| Deployment | Exact ID | Upstream | Access | State |
| --- | --- | --- | --- | --- |
| `gpt-5.3-codex` | `83500e6b-6faf-44c8-a4d2-d557f72d11ec` | `chatgpt/gpt-5.3-codex` | direct; two teams | unblocked |
| `chatgpt/gpt-5.3-codex` | `72c9e569-3317-4412-ba67-566e172b295d` | `chatgpt/gpt-5.3-codex` | direct; two teams | unblocked |
| `chatgpt-account2/gpt-5.3-codex` | `94126f16-fdbb-48e7-9586-b8a1a68719d5` | `chatgpt/gpt-5.3-codex`, account2 profile | direct; two teams | unblocked |
| `defend/gpt-5.5` | `67c996f8-38d7-4406-833b-601735d8a364` | protected OpenAI-compatible upstream | direct; two teams | unblocked |

Fresh NAS normal GPT-5.3 dependency:

```text
gpt-5.3-codex -> chatgpt-account2/gpt-5.3-codex, chatgpt/gpt-5.3-codex
```

Fresh NAS `defend/gpt-5.5` dependencies include an outbound fallback to `chatgpt/gpt-5.5` and inbound references from `minimax-m3-v0-nvfp4-reap50`, `minimax-m2.7`, `chatgpt/gpt-5.5`, and `chatgpt/gpt-5.4-mini`. These exact dependencies were enumerated but not changed

## Defaults And Router State

- Neither host has a default model or model-group alias resolving a retired normal GPT-5.3 name
- Neither host has context-window or content-policy fallback references to the targets
- Access membership, blocked state, direct-access state, deployment identities, model/group projections, and complete router settings are retained only in protected host-local snapshots
- The unauthenticated method assumption `GET /fallback` was rejected with HTTP 405; exact fallback state was instead proven by authenticated `/router/settings` and model-specific authenticated `GET /fallback/{model}` checks
