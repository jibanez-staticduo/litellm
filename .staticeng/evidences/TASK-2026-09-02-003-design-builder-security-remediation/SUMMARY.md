# TASK-2026-09-02-003 Evidence Summary

## Summary

PASS for research. TASK-011 Reopen 3's six builder High matches are fully attributed: two advisories affect one setuptools 68.1.2 PEP 517 build-cache artifact selected by `ml-dtypes 0.4.1`; quinn-proto 0.11.14 and rustls-webpki 0.103.10 each appear twice because uv 0.11.7 copied separate auditable `uv` and `uvx` binaries. The final image contains none of the six and reports zero High/Critical

The minimal proposed correction is a root uv build constraint `setuptools>=78.1.1`, a generated `uv.lock` refresh, and a root Dockerfile uv input bump to official uv 0.11.26 index `sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`, requiring amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`. That release carries quinn-proto 0.11.15 and rustls-webpki 0.103.13. LiteLLM's application `Cargo.lock` already carries fixed 0.11.16 and 0.103.13, so changing it would not remediate the scanned uv binaries

## Work Performed

- Read the governing SCR, TASK-011 Reopen 3 task, summary, machine-readable SPDX/CycloneDX SBOMs and Grype scans, current Docker/Python/Rust locks, nearest CodeMaps, and prior release/security designs
- Mapped all six raw matches to package, advisory, source layer, build stage, owning input, fixed version, duplicate cause, and final-image presence
- Proved the vulnerable setuptools is absent from `/app/.venv` and remains only in the builder's uv cache because `ml-dtypes 0.4.1` declares exact build requirement `setuptools~=68.1.0`
- Verified official uv 0.11.26 upstream lock versions, immutable release identity, exact OCI index/amd64 child, GitHub artifact attestation availability, and the upstream advisory remediation commit
- Defined the three-file implementation boundary, source/runtime regression matrix, new immutable builder/final SBOM and same-database scan gates, expected six-match delta, cleanup, rollback, and arm64 exclusion
- Defined digest-only private-registry signing and verification for both builder and final with SPDX, CycloneDX, and SLSA v1 attestations, strict subject/predicate checks, secret-safe credential handling, and fail-closed signer/referrer policy

## High Map

| Count | Package | Advisory | Vulnerable | Fixed | Owner | Final |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | setuptools | `GHSA-cx63-2mw6-8hw5` | 68.1.2 | 70.0.0; effective 78.1.1 | root uv build constraint / generated lock | absent |
| 1 | setuptools | `GHSA-5rjg-fvgr-3xxf` | 68.1.2 | 78.1.1 | root uv build constraint / generated lock | absent |
| 2 | quinn-proto | `GHSA-4w2j-m93h-cj5j` | 0.11.14 in uv and uvx | 0.11.15 | root Dockerfile `UV_IMAGE` / upstream uv lock | absent |
| 2 | rustls-webpki | `GHSA-82j2-j2ch-gfr8` | 0.103.10 in uv and uvx | 0.103.13 | root Dockerfile `UV_IMAGE` / upstream uv lock | absent |

The exact detailed location/layer ledger, commands, policy, and signed handoff are in `.staticeng/tasks/done/TASK-2026-09-02-003-design-builder-security-remediation.md`

## Signing Decision

The procedure is executable with an approved KMS/HSM key, a self-managed private key matching a PMA-approved public key, or a keyless identity frozen to exact issuer/workflow claims. The repository tracks `cosign.pub` with SHA-256 `ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3`, but this research did not identify or invent an authorized private-key owner. PMA must name the signer before publication

Builder and final must be published only under unique quarantine tags, resolved to exact `docker.staticduo.com/litellm@sha256:<manifest>` references, and checked so registry config digest equals retained local image ID. Both exact digests receive a Cosign signature plus SPDX JSON, CycloneDX JSON, and SLSA provenance v1 attestations. Fresh verification must validate key/identity, Cosign claims, annotations, exact subject digest, predicate type/content, and registry discoverability. Registry credentials and all private signing material remain outside repository evidence

## Acceptance Criteria Coverage

- **AC-1: PASS.** Every High is mapped to provenance, stage, owner, fix, duplicate semantics, and final-image absence
- **AC-2: PASS.** One build constraint fixes setuptools; one uv input bump fixes both duplicate Rust pairs; application Cargo and behavior remain unchanged
- **AC-3: PASS.** Exact source/input boundaries, regressions, immutable identities, SBOM/scans, expected delta, rollback, cleanup, and arm64 boundary are specified
- **AC-4: PASS FOR POLICY DESIGN.** The private-registry procedure is executable and secret-safe once PMA names the signer. Absence of an approved signer still blocks execution
- **AC-5: PASS.** Task and evidence contain the signed implementation-ready handoff. No source, build, push, sign, registry, host, production, or deployment mutation occurred

## Documentation Impact

No product or application architecture documentation update is required. This task is the bounded remediation policy. A maintained signer/KMS, release script, immutable APK mirror, or foundation-image mechanism requires a separate architecture/docs task and CodeMap updates

## Open Risks

- `ml-dtypes 0.4.1` explicitly requires setuptools `~=68.1.0`, so the safe additive build constraint may fail resolution; failure requires PMA-routed dependency/override review, not a forced silent bypass
- The proposed uv image has read-only provenance and lock evidence but no candidate-bound scan or runtime evidence yet
- No approved private signer or keyless identity is currently named, so signing remains blocked
- Mutable Wolfi APK resolution, arm64, promotion, stable tags, Fedora, NAS, and deployment remain outside this authorization

## Recommended Next Step

PMA should approve a signer identity and activate TASK-2026-09-02-004 with the exact three-file boundary. After independent review and push of a passing correction, reopen TASK-011 against entirely new builder/final subjects and execute the complete signing/attestation procedure before any release task

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Authorize only the root setuptools build constraint, generated uv lock, and digest-pinned uv 0.11.26 Docker input described in the task. Do not change application Cargo. Rebuild and requalify new exact amd64 builder/final subjects, require zero fixable High/Critical, then sign and attach SPDX, CycloneDX, and SLSA v1 attestations to both private-registry digests using a PMA-approved identity. Signing remains blocked until that signer is named. Keep promotion, stable tags, Fedora, NAS, and deployment unauthorized

## Reopen History

### Reopen 1 - Confirmed build constraint conflict

TASK-004 proved that `ml-dtypes 0.4.1` exact build metadata requires setuptools `<68.2.dev0`, so the prior global `setuptools>=78.1.1` design is invalid and remains historical only. The task rolled back all candidate files and produced no new builder/final subjects

### Reopen 1 Result

PASS for revised research. Current chain is LiteLLM 1.100.0 extra-proxy -> RedisVL 0.4.1 -> ml-dtypes 0.4.1. RedisVL 0.5.2 first widens ml-dtypes to `<1.0.0`, proving upstream support, but that RedisVL upgrade also changes semantic-cache, vectorizer, schema, filter and query behavior. The minimal correction keeps RedisVL 0.4.1 and uses uv 0.11.26's package-scoped runtime override to select exact ml-dtypes 0.5.4

The executable correction is:

- Root `pyproject.toml`: add scoped override `{ package = { name = "redisvl", version = "0.4.1" }, dependencies = ["ml-dtypes==0.5.4"] }`, `no-build-package = ["ml-dtypes"]`, and require uv `>=0.11.26,<0.11.27`; do not add a setuptools build constraint
- Root `uv.lock`: regenerate with uv 0.11.26; expected package delta is only ml-dtypes 0.4.1 -> 0.5.4, with RedisVL 0.4.1, NumPy and unrelated packages unchanged
- Root `Dockerfile`: retain approved uv 0.11.26 index `sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`, amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`, and clean uv cache only after the wheel-only installation and all build outputs finish
- CI callers: PMA must approve changing repository-controlled uv 0.10.9 pins to 0.11.26 because uv 0.10.9 cannot parse scoped override syntax; do not land incompatible project metadata
- Application Cargo remains byte-identical

For amd64 CPython 3.13, required wheel is `ml_dtypes-0.5.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`, SHA-256 `533ce891ba774eabf607172254f2e7260ba5f57bdd64030c9a4fcfbd99815d0d`, metadata SHA-256 `51b5729b48ce71736748bbf43d4f355485f42b44977d6016717bbd6b11b7dfc0`. PyPI PEP 740 provenance identifies GitHub repository `jax-ml/ml_dtypes`, workflow `wheels.yml`, release environment and the exact wheel subject/hash. Tag `v0.5.4` resolves through annotated tag `882eb0f8d64a13696122945e4fb276e3cbf52ce8` to commit `9fd1a480f1cdb23b3d28dfea5eadf3d84b6dfc62`

Required regressions include full Redis/Valkey semantic-cache suites, real Redis sync/async store/check/TTL/filter/isolation/reconnect, bfloat16 byte and existing-index compatibility, normal source/Rust/UI gates, exact clean builder/final runtime qualification, and new SPDX/CycloneDX plus same-frozen-current-DB scans. Acceptance remains zero Critical and zero fixable High, with no setuptools 68.1.2, ml-dtypes sdist/build environment, vulnerable uv/uvx Rust crates, ignore rule or cache-path exclusion

The detailed Python 3.10-3.14 wheel hashes, alternative analysis, stop gates, rollback and signed handoff are in `.staticeng/tasks/done/TASK-2026-09-02-003-design-builder-security-remediation.md`

### Reopen 1 Acceptance Criteria Coverage

- **AC-1: PASS.** Upstream dependency chain, releases, behavior deltas, wheel matrix, hashes and provenance are mapped
- **AC-2: PASS.** One exact minimal correction is selected without global setuptools override, RedisVL upgrade or Cargo change
- **AC-3: PASS.** Files, versions/digests, CI uv alignment, tests, scans, stop gates and rollback are executable
- **AC-4: PASS UNCHANGED.** Signing remains fail-closed pending an approved identity
- **AC-5: PASS.** Research-only task/evidence update is complete; no product/build/release mutation occurred

### Reopen 1 Open Risks

- PMA must authorize CI uv pin alignment from 0.10.9 to 0.11.26
- RedisVL 0.4.1 did not publish the widened bound, so upstream proof from 0.5.2 must be backed by real compatibility tests
- ml-dtypes 0.5.3 introduced pickle incompatibility; the reviewed path uses raw vector bytes, but this must be verified against existing Redis index behavior
- Signing identity remains unresolved

### Reopen 1 Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS Reopen 1 investigation. Use uv 0.11.26 to scope RedisVL 0.4.1's ml-dtypes requirement to exact 0.5.4, enforce wheel-only installation, retain the approved uv OCI digest, and keep RedisVL, NumPy, application Cargo and product code unchanged. Require the attested amd64 wheel SHA-256 `533ce891ba774eabf607172254f2e7260ba5f57bdd64030c9a4fcfbd99815d0d`, full semantic-cache/vector-byte/runtime regressions, and zero Critical/fixable High scans. PMA must approve CI uv 0.11.26 alignment before implementation. Keep signing, publication, Fedora, NAS and deployment blocked
