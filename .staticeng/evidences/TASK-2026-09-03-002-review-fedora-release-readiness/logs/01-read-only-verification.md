# Read-Only Verification Ledger

## Scope And Safety

- Review date: 2026-09-03
- Repository, local Docker, registry-name resolution, GitHub metadata, and Fedora checks were read-only
- No image was built, pulled, pushed, tagged, signed, or deleted
- No registry referrer, tag, manifest, configuration, database, container, service, host file, Git ref, stable selector, or NAS object was mutated
- No secret value, token, private key, authorization material, environment value, request content, response content, raw private log, database row, or credential filename was read into evidence

## Source And Candidate

```text
local main: 445877a1243b10af2457a2f363cc54d6b31208a9
origin/main: 445877a1243b10af2457a2f363cc54d6b31208a9
qualified source: bf58974a935521fa570fa7e280c51a00b2e5b54e
qualified source is direct parent of main: yes
non-StaticEng changes after qualified source: 0
qualified source tree: 5bb1b3185d25ba851482ee022503178996df3341
builder: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac amd64
final: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915 amd64
builder/final revision label: bf58974a935521fa570fa7e280c51a00b2e5b54e
builder/final task label: TASK-2026-09-01-011-r6
```

The Reopen 6 SHA-256 manifest verifies all 21 retained artifacts. Parsed scan counts match the evidence summary:

```text
subject   Critical  High  Medium  Low  Unknown
builder          0     0      11    1        4
final            0     0       9    1        2
base             0     0       1    0        0
uv               0     0       0    0        0
Grype database schema: v6.1.9
Grype database built: 2026-09-03T06:30:55Z
```

Cleanup was independently rechecked: zero `task011r6-*` containers, networks, volumes, builders, and worktrees remain. Both exact retained release images are present

## Signing And Publication

```text
repository cosign.pub file SHA-256: ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3
repository cosign.pub SPKI SHA-256: c08f854f070d28a9fc5f64ffc7033507f420084b564c906c0e8a9ea45af90b6b
key origin: upstream BerriAI commit 0112e53046018d726492c814b3644b7d376029d0
unchanged from frozen upstream snapshot: yes
local Cosign binary: absent
local signer environment names: none
repository alternate Cosign/signing/key files: none
fork Actions secret names: none
fork Actions variable names: none
fork Actions environment names: none
approved StaticDuo KMS/HSM URI: not named
approved StaticDuo keyless issuer/workflow identity: not named
```

The configured Git SSH commit signing key is a different purpose and is not an approved container signing identity. No publication or signing action was attempted

Reserved unique publication handles were unresolved at review time:

```text
docker.staticduo.com/litellm:quarantine-task011-r6-builder-bf58974a9355-eb673f1c4f02
docker.staticduo.com/litellm:quarantine-task011-r6-final-bf58974a9355-ad33017b518b
```

These handles do not qualify as immutable subjects. The later authorized publisher must resolve and freeze their registry manifests, prove each manifest config equals its retained local image ID, sign the digest subjects, attach all six attestations, and freshly verify registry persistence

## Fedora Baseline

```text
host: fedora
stack: /home/staticduo/docker/litellm
selector count: 1
selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
image/config ID: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
OCI revision: 64a3b83bf0bdd8813890d20ba7b6b57fc034bb95
platform: amd64
runtime: running, healthy, restart 0, OOM false
host-local readiness/liveliness: 200/200
public readiness/liveliness: 200/200
model rows: 26
model projection SHA-256: 98f0d541823b9f7c19c0a19d338e2f9027b07b6801015d2aeb5ab739229e6231
fallback rules: 24
fallback projection SHA-256: a057787927e9cfb8f5b140f7b4ed7e7f90f792e88fdc86b84d0ffdb7cf2c0f0c
default/account2 qualified aliases: 6/6
account3 references: 0
cross-profile fallback: true
MCP registrations: 13
MCP states: 11 healthy, 1 auth-required, 1 unknown
```

PostgreSQL, Redis, admin MCP, and compat admin MCP containers are running/healthy with restart 0 and OOM false. The current selector is inspectable locally. Protected Compose/config/wrapper hashes exactly match the 2026-09-01 architecture baseline. `.env` remains owner-readable mode 0600, and all protected paths are regular files

Fedora has no database dump in its release hierarchy. A zero-output `pg_dump` read confirms current dump access, and `pg_restore` is installed. This proves feasibility only; it is not the required protected backup, checksum, listing, or disposable restore rehearsal

## Migration Gap

The candidate contains ten proxy-extras migrations absent from Fedora's current source revision. Evidence proves all 161 candidate migrations on an empty PostgreSQL database and an idempotent restart only. No evidence upgrades a secret-safe current-Fedora schema fixture or starts the prior Fedora image against the upgraded schema

Two new migrations include bounded or conditional row updates:

- `20260817000000_shadow_eval_multi_key` fills `group_id`, then makes it non-null
- `20260818224500_add_shadow_eval_stopped_by` updates selected stopped shadow-eval jobs

Schema inspection alone cannot substitute for required upgrade and prior-image compatibility execution. This remains fail-closed

## Validation

```text
staticeng_validate: PASS
warnings: 0
```

## Verdict

REJECT. Exact qualification and current Fedora stability pass, but mandatory signing identity, immutable registry publication/signature/attestation chain, current-schema upgrade/prior-image rollback compatibility, and fresh DB backup/restore evidence are absent
