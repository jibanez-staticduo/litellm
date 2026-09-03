---
id: TASK-2026-09-02-003-design-builder-security-remediation
complexity: complex
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-02-004-fix-builder-security
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 1
---

# Task: Design builder security remediation

## Objective

Define the smallest deterministic remediation for all six fixable High findings in the exact candidate builder and establish an executable digest-signing/attestation procedure.

## Acceptance Criteria

- [x] AC-1: Map every builder High to package provenance, build stage, fixed version, lock/source owner, and final-image presence.
- [x] AC-2: Define minimal setuptools, quinn-proto, and rustls-webpki corrections without weakening reproducibility or application behavior.
- [x] AC-3: Define exact source/lock/Docker inputs, regression tests, SBOM/scan expectations, and rollback.
- [x] AC-4: Determine an executable approved signing/attestation policy using the private registry without persisting secrets in repository evidence.
- [x] AC-5: Update task/evidence with signed implementation-ready handoff; no mutations.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-011 Reopen 3 machine-readable scans and current Docker/Cargo/Python locks. Research only. Identify exact vulnerable components and minimal safe fixed versions, including duplicate matches and upstream status. Define a secure executable signing path; no source/build/push/sign/deploy mutations. Return exact implementation handoff.

# Post Implementation Task Updates

## Technical Architect: Post Investigation Expectations

### Summary

PASS for investigation. The six builder High matches reduce to three vulnerable package/version/advisory tuples. Two setuptools advisories are one cached PEP 517 build dependency, and the four Rust matches are two advisories duplicated across the copied `uv` and `uvx` binaries. None is present in the final image

The smallest correction is two bounded input changes, not edits to LiteLLM's Rust lock. Add root `[tool.uv].build-constraint-dependencies = ["setuptools>=78.1.1"]`, then regenerate `uv.lock` with the repository-pinned uv line so the isolated `ml-dtypes 0.4.1` build cannot select vulnerable setuptools 68.1.2. Replace only root `Dockerfile` `UV_IMAGE` with a digest-pinned official uv release at least 0.11.26. The frozen recommended release is `ghcr.io/astral-sh/uv:0.11.26@sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`, whose amd64 child is `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a` and upstream lock contains quinn-proto 0.11.15 plus rustls-webpki 0.103.13. Do not edit `litellm-rust/Cargo.lock`: current application entries are already quinn-proto 0.11.16 and rustls-webpki 0.103.13

Candidate signing is executable only after PMA names an authorized signer for the repository's existing `cosign.pub` key or supplies an approved KMS/keyless identity. This investigation approves the procedure and trust contract, not an unknown private key. Sign and attest both exact private-registry builder and final digest subjects. A missing signer, public-key mismatch, registry referrer failure, or predicate/subject mismatch remains a fail-closed blocker

### High Finding Map

All rows come from Reopen 3 builder `sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104`, Syft builder SBOMs, and frozen Grype 0.118.0 DB schema 6.1.9 built `2026-09-02T06:35:12Z`

| Scan match | Provenance and stage | Owner | Required correction | Final |
| --- | --- | --- | --- | --- |
| setuptools 68.1.2, `GHSA-cx63-2mw6-8hw5`, fixed 70.0.0 | `/root/.cache/uv/archive-v0/.../setuptools-68.1.2.dist-info`; layer `sha256:d75d8309...`; first frozen `uv sync`; isolated build dependency from `ml-dtypes 0.4.1` exact `setuptools~=68.1.0` | root `pyproject.toml` build constraint and generated `uv.lock`; not the runtime setuptools 83.0.0 lock entry | add build constraint `setuptools>=78.1.1`, which covers both advisories; regenerate lock and prove build cache contains no `<78.1.1` setuptools | absent; final has zero High/Critical |
| setuptools 68.1.2, `GHSA-5rjg-fvgr-3xxf`, fixed 78.1.1 | same artifact and layer as prior row; second advisory, not a duplicate scan location | same | same, with 78.1.1 as the effective minimum safe version | absent |
| quinn-proto 0.11.14, `GHSA-4w2j-m93h-cj5j`, fixed 0.11.15 | cargo-auditable data embedded in copied `/usr/local/bin/uv`; uv copy layer `sha256:c65bfea943...` | root `Dockerfile` `UV_IMAGE`, upstream uv release lock | replace uv 0.11.7 with digest-pinned uv >=0.11.26; recommended 0.11.26 is the first inspected 0.11 release carrying 0.11.15 | absent |
| quinn-proto 0.11.14, same advisory | same upstream package duplicated in copied `/usr/local/bin/uvx`; uvx copy layer `sha256:13a69395b1...` | same | same single uv image bump removes both matches | absent |
| rustls-webpki 0.103.10, `GHSA-82j2-j2ch-gfr8`, fixed 0.103.13 | cargo-auditable data embedded in copied `/usr/local/bin/uv`; uv copy layer `sha256:c65bfea943...` | root `Dockerfile` `UV_IMAGE`, upstream uv release lock | same uv bump; uv 0.11.26 carries 0.103.13 | absent |
| rustls-webpki 0.103.10, same advisory | same upstream package duplicated in copied `/usr/local/bin/uvx`; uvx copy layer `sha256:13a69395b1...` | same | same single uv image bump removes both matches | absent |

The repository runtime lock already selects setuptools 83.0.0. The vulnerable 68.1.2 is not installed in `/app/.venv`; an offline probe raises `ModuleNotFoundError` for setuptools while the stale build cache remains scan-visible. Removing the cache alone would hide the vulnerable tool without correcting the build input, so it is not an accepted remediation

The root application Rust lock at the exact Reopen 3 source already carries quinn-proto 0.11.16 and rustls-webpki 0.103.13. Those versions are separate from the uv/uvx cargo-auditable manifests and require no application Cargo edit. Upstream uv 0.11.26 commit `cfa5ca8122dbdf9cc3950724500a882823102435` explicitly bumped quinn-proto for the advisory. Official uv 0.11.26 has an immutable release and GitHub artifact attestations

### Exact Implementation Contract

1. Start from reviewed fork-main commit `165a94ecfbf21d7ff4626815ac6b298ac34e2adb`; preserve root Dockerfile Wolfi build/runtime index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`, Rust index `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`, UI index `sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43`, Python 3.13.15-r4 pins, all extras, and all stage boundaries
2. Change only root `pyproject.toml`, generated `uv.lock`, and root `Dockerfile`. Add `build-constraint-dependencies = ["setuptools>=78.1.1"]` under `[tool.uv]`; retain the existing runtime `constraint-dependencies` entry `setuptools>=83.0.0`. Regenerate, never hand-edit, `uv.lock`; accept only build-constraint metadata plus resolver-required lock changes. If the pinned uv cannot represent the build constraint deterministically, stop instead of using an uncommitted CLI constraint
3. Replace `UV_IMAGE` only with `ghcr.io/astral-sh/uv:0.11.26@sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`; require amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`. Retain both `/uv` and `/uvx` copies and existing sync flags. Re-resolve the tag immediately before implementation and reject any identity mismatch
4. Verify uv provenance against its exact digest using `gh attestation verify oci://ghcr.io/astral-sh/uv@sha256:3d868e... --owner astral-sh`; record sanitized success and release/source identities. Digest plus verified GitHub SLSA provenance is the approved alternate publisher provenance where a standalone Cosign signature is absent
5. Do not update `litellm-rust/Cargo.toml`, `litellm-rust/Cargo.lock`, package behavior, base images, Python, Rust, Node, application dependencies, alternate Dockerfiles, entrypoints, deployment files, registry stable tags, or production state. Any extra source/lock churn returns to PMA for review

### Regression And Security Qualification

Before commit, require `git diff --check`, `uv lock --check`, clean `uv sync --frozen` for the candidate extras, and an exact lock diff review. Run mapped Python quality gates affected by `pyproject.toml`/`uv.lock`, plus import/smoke checks for `ml_dtypes`, `redisvl`, semantic-router, LiteLLM, the native Rust bridge, uvloop, Prisma, and the normal entrypoint. Run `cargo fmt --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, Bedrock-feature Clippy, `cargo test --workspace --locked`, and Bedrock-feature tests even though application Cargo input must remain byte-identical. Run Admin UI `npm ci`, formatting, lint, type, unit, knip, and production build because the root image rebuild recompiles the UI

Build exact clean `linux/amd64` builder and final targets from committed defaults with no build-argument substitutions. Verify source labels, platform, toolchain assertions, both frozen syncs, native build, Prisma generation, migration from empty DB and idempotent restart. Rerun the TASK-011 isolated model, Responses, MCP/LazyMCP/OAuth, permission, reconnect, candidate-bound real-tool, log-redaction, preservation, production-identity, cleanup, and no-secret gates. Prior Reopen 3 functional success is regression guidance only and cannot qualify new identities

Generate durable SPDX JSON and CycloneDX JSON SBOMs for selected Wolfi base, exact builder, and exact final; include the uv input SBOM/provenance evidence. Scan old builder, new builder, and new final with one newly frozen, current Grype DB and retain machine-readable JSON plus SHA-256 manifest. Acceptance requires zero Critical and zero fixable High for builder and final, no setuptools below 78.1.1 in build/cache evidence, no quinn-proto below 0.11.15 or rustls-webpki below 0.103.13 in uv or uvx, and independent disposition of every remaining/new High. Do not deduplicate raw results; the expected delta is exactly six removed matches accounted for by the table above

### Private Registry Signing And Attestation Policy

The approved trust root is a PMA-authorized StaticDuo release signer, not merely whoever can push to `docker.staticduo.com`. Preferred key source is an approved KMS/HSM URI accessible only to the release operator. A self-managed key is acceptable only if its public half exactly matches a PMA-approved repository trust root; this repository already tracks `cosign.pub` with SHA-256 `ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3`, but the private-key owner/location is not established by this task. Keyless is acceptable only with an explicitly frozen issuer and exact workflow identity. Interactive developer OIDC is not accepted

Both builder and final must first be published under unique quarantine identities in `docker.staticduo.com/litellm`, then resolved and operated on only as `docker.staticduo.com/litellm@sha256:<manifest>`. Before signing, prove each registry manifest's config digest equals its retained local image ID. Do not sign local config IDs, tags, rejected Reopen 3 subjects, or a rebuilt equivalent. Registry credentials come from the operator's existing Docker credential helper or secret manager and must never appear as command arguments, logs, environment dumps, task text, or evidence

The release operator substitutes only non-secret placeholders below and uses checksum-verified Cosign 3.1.3. `SIGNING_KEY` is an approved KMS URI or owner-only private-key path outside the repository. No `--allow-insecure-registry`, `--allow-http-registry`, `--check-claims=false`, or insecure verification flag is permitted

```bash
export BUILDER_REF='docker.staticduo.com/litellm@sha256:<builder-manifest>'
export FINAL_REF='docker.staticduo.com/litellm@sha256:<final-manifest>'
export SIGNING_KEY='<approved-kms-uri-or-owner-only-key-path>'
export PUBLIC_KEY='<approved-public-key-path>'

cosign sign --yes --key "$SIGNING_KEY" \
  -a staticeng.task=TASK-2026-09-01-011 \
  -a org.opencontainers.image.revision='<full-source-commit>' "$BUILDER_REF"
cosign sign --yes --key "$SIGNING_KEY" \
  -a staticeng.task=TASK-2026-09-01-011 \
  -a org.opencontainers.image.revision='<full-source-commit>' "$FINAL_REF"

cosign attest --yes --key "$SIGNING_KEY" --type spdxjson \
  --predicate '<builder.spdx.json>' "$BUILDER_REF"
cosign attest --yes --key "$SIGNING_KEY" --type cyclonedx \
  --predicate '<builder.cyclonedx.json>' "$BUILDER_REF"
cosign attest --yes --key "$SIGNING_KEY" --type slsaprovenance1 \
  --predicate '<builder.slsa-provenance-v1.json>' "$BUILDER_REF"
cosign attest --yes --key "$SIGNING_KEY" --type spdxjson \
  --predicate '<final.spdx.json>' "$FINAL_REF"
cosign attest --yes --key "$SIGNING_KEY" --type cyclonedx \
  --predicate '<final.cyclonedx.json>' "$FINAL_REF"
cosign attest --yes --key "$SIGNING_KEY" --type slsaprovenance1 \
  --predicate '<final.slsa-provenance-v1.json>' "$FINAL_REF"

cosign verify --key "$PUBLIC_KEY" \
  -a staticeng.task=TASK-2026-09-01-011 \
  -a org.opencontainers.image.revision='<full-source-commit>' "$BUILDER_REF"
cosign verify --key "$PUBLIC_KEY" \
  -a staticeng.task=TASK-2026-09-01-011 \
  -a org.opencontainers.image.revision='<full-source-commit>' "$FINAL_REF"
for ref in "$BUILDER_REF" "$FINAL_REF"; do
  cosign verify-attestation --key "$PUBLIC_KEY" --type spdxjson "$ref"
  cosign verify-attestation --key "$PUBLIC_KEY" --type cyclonedx "$ref"
  cosign verify-attestation --key "$PUBLIC_KEY" --type slsaprovenance1 "$ref"
  cosign tree "$ref"
done
```

Verification must parse each returned DSSE statement, require the expected predicate type, require the sole image subject digest to equal the requested registry manifest, and check provenance fields against the exact source commit/tree, Dockerfile and lock hashes, platform, base/toolchain digests, build arguments, builder/final config IDs, and qualification artifact checksums. Cryptographic verification without predicate validation is insufficient. Retain sanitized verification JSON, referrer inventory, public-key fingerprint, non-secret signer identifier, manifest/config identities, predicate SHA-256 values, and command exit statuses. Retain no registry token, private key, key password, OIDC token, KMS credential, Docker config, or unredacted environment

Use Cosign's default registry storage first. If `docker.staticduo.com` does not support the attempted OCI referrer mode, retry the Cosign-supported legacy signature-tag mode while keeping the exact digest subject. `COSIGN_DOCKER_MEDIA_TYPES=1` is a compatibility fallback only, not a TLS bypass. Validate discoverability with `cosign tree` and fresh-process verification. Any registry that cannot persist and return all six attestations and both signatures blocks release; do not substitute evidence-only bundles without a separately approved policy

### Rollback

Before publication, rollback is one atomic revert of the root Dockerfile, root pyproject, and generated uv lock changes, deletion of all failed disposable builders/images/caches, and retention of the Reopen 3 rejection as historical evidence. Do not partially revert the uv bump while retaining provenance claims for the new digest, or remove build caches as a vulnerability workaround

After quarantine publication but before deployment, rollback deletes or permanently quarantines only the new unique candidate tags/referrers according to registry retention policy; it never moves stable and never reuses the rejected digest. After a separately authorized deployment, restore the exact pre-deployment Fedora manifest captured immediately before mutation and rerun readiness, migrations, model inventory, Responses, MCP/LazyMCP, real-tool behavior, identity, and logs. This remediation adds no schema change, but upstream migration compatibility remains a release gate. NAS remains untouched

### Impact And CodeMap Surface

Implementation affects root `Dockerfile`, root `pyproject.toml`, and generated root `uv.lock`. Root `.staticeng/codemap.yml` is the nearest navigation map. No module boundary, entrypoint, route, API, schema, or command changes, so no CodeMap content change is required unless implementation adds a maintained script or workflow. `litellm-rust/codemap.yml` is read-only impact context because its lock must not change. If the signing procedure becomes a maintained repository script or steady-state release policy, route a separate docs/tooling task and index it in the applicable CodeMap

### Acceptance Criteria Coverage

- **AC-1: PASS.** Six raw matches are mapped to three package/advisory tuples, exact uv/uvx/cache locations and layers, upstream or root-lock ownership, safe versions, duplicate semantics, and final-image absence
- **AC-2: PASS.** The minimal changes are one root build constraint plus regenerated uv lock for setuptools and one digest-pinned uv input bump for both Rust advisories; application Cargo and product behavior remain unchanged
- **AC-3: PASS.** Exact source/input boundaries, version/digest floors, regression matrix, newly frozen SBOM/scan policy, expected six-match delta, evidence, cleanup, and rollback are defined
- **AC-4: PASS FOR POLICY DESIGN.** A private-registry digest-only signing/attestation/verification contract is executable with an approved KMS, matching existing key, or frozen keyless identity. Execution remains blocked until PMA names that signer; no identity was invented and no secret is persisted
- **AC-5: PASS.** Task and secret-free Evidence Packet contain this signed implementation-ready handoff. Research used read-only source, image metadata, retained evidence, and official documentation only; no source, lock, build, push, sign, registry, host, production, or deployment mutation occurred

### Documentation Impact

No product or application architecture documentation change is required. This task is the implementation and release-policy truth for the bounded remediation. A maintained signer, release script, KMS integration, immutable APK mirror, or foundation image is a separate steady-state architecture change and must be documented under `docs/architecture/` with its own CodeMap updates

### Open Risks

- The setuptools constraint conflicts with `ml-dtypes 0.4.1`'s declared `setuptools~=68.1.0`; uv may fail closed. If so, PMA must authorize a compatible `ml-dtypes`/`redisvl` dependency update or a separately reviewed scoped build override. Do not silently force an incompatible backend
- The uv 0.11.26 index and amd64 child were resolved read-only and upstream locks were inspected, but the new uv image has not been scanned in the exact candidate builder. Any new fixable High or functional regression rejects it
- The repository contains a public verification key but this task found no approved private-key owner, KMS URI, or frozen keyless identity. Signing remains blocked until PMA or the security owner supplies one
- Public Wolfi APK resolution remains retention-bound and mutable as documented by TASK-001. This task does not create the separately recommended immutable APK mirror or foundation images
- Arm64 remains unauthorized. All identities and regression requirements here are for `linux/amd64`

### Recommended Next Step

PMA should obtain security-owner approval for the signer identity and public-key fingerprint, then activate TASK-2026-09-02-004 with the exact three-file boundary. Developer should first test whether the safe setuptools build constraint resolves without overriding `ml-dtypes` metadata, then apply the uv 0.11.26 digest bump, run the complete source/build/security matrix, and return the exact diff for Tech Lead review. After the reviewed commit is pushed, reopen TASK-011 from the beginning against wholly new builder/final identities. Keep TASK-012, Fedora, NAS, stable tags, and deployment blocked

### Technical Architect Review Note

AC-1 through AC-5 are design-covered. The design separates the one real setuptools build artifact and two uv/uvx duplicate pairs, avoids an ineffective application Cargo edit, and makes signature verification fail closed on subject, identity, predicate, registry persistence, and secret handling. No source, build, push, signing, registry, production, or deployment action was performed

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Authorize TASK-2026-09-02-004 only for root `pyproject.toml`, generated `uv.lock`, and root `Dockerfile`: constrain isolated build setuptools to at least 78.1.1, and replace uv 0.11.7 with digest-pinned official uv 0.11.26 index `sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5` requiring amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`. Do not edit application Cargo; its quinn-proto 0.11.16 and rustls-webpki 0.103.13 are already fixed. Rebuild and rerun all source, functional, SBOM, same-database scan, provenance, cleanup, and rollback gates against new immutable subjects. Publish builder and final only to unique private-registry quarantine digests, then sign and attach SPDX, CycloneDX, and SLSA v1 attestations to both using a PMA-approved signer whose public identity is frozen before execution. Signing remains blocked until that identity is named. Reject any constraint conflict, extra lock drift, registry/referrer failure, subject or predicate mismatch, fixable High/Critical, missing attestation, secret exposure, Fedora/NAS mutation, stable-tag movement, or deployment

## Reopen History

### Reopen 1 - Replace impossible global build floor

[Agent Message] From: product_manager To: technical_architect

Reopen TASK-003 after implementation proved the global setuptools floor conflicts with ml-dtypes 0.4.1 exact metadata. Research current upstream ml-dtypes/redisvl dependency chain and alternatives: compatible package upgrades with behavior impact, package-scoped build constraint/override supported by current uv, prebuilt wheel strategy, immutable wheelhouse, or builder cache exclusion only if it truly removes vulnerable executable inputs. Do not weaken zero-fixable-High policy or edit application Cargo unnecessarily. Update the original task/evidence Reopen History with one exact executable remediation, files, versions/digests, tests/scans/rollback. No edits/build/push/sign/deploy

### Reopen 1 Result

PASS for revised investigation. TASK-004 proved the global `setuptools>=78.1.1` build constraint unsatisfiable because `ml-dtypes 0.4.1` declares `setuptools>=68.1.0,<68.2.dev0`. The exact revised remediation is to update only the transitive runtime package to `ml-dtypes==0.5.4`, require wheels only for that package, regenerate `uv.lock`, and keep the approved uv 0.11.26 Docker input. Do not add any setuptools build constraint or override and do not update RedisVL

#### Current Chain And Upgrade Choice

Current lock chain is `litellm[extra-proxy] 1.100.0` -> `redisvl 0.4.1` -> `ml-dtypes 0.4.1`. RedisVL 0.4.1 explicitly requires `ml-dtypes>=0.4.0,<0.5.0`, which is why the unlocked project range alone does not advance it. RedisVL 0.5.2 is the first release widening that dependency to `<1.0.0`, but it also includes the RedisVL 0.5.1 feature release: changed vectorizer APIs, client validation, schema validation, filters, query behavior and semantic-cache code. RedisVL 0.6.0 adds still more lazy-import and semantic-cache changes. Upgrading RedisVL therefore has much larger observable behavior and regression scope than needed

`ml-dtypes 0.5.4` is selected instead of 0.5.0, 0.5.1, 0.5.3, or 0.6.0. It is the latest 0.5 line, keeps Python >=3.9 and NumPy compatibility, publishes CPython 3.10 through 3.14 Linux wheels for x86_64 and aarch64, and its source build uses fixed setuptools `~=80.9.0`. Version 0.6.0 switches to CMake/scikit-build-core, drops Python 3.9 and NumPy <2, so it broadens compatibility risk unnecessarily. The 0.5 line adds new low-precision dtypes and fixes casts/arithmetic; 0.5.3 changes pickle compatibility for values serialized by earlier releases. LiteLLM/RedisVL use `bfloat16` conversion to Redis vector bytes, not Python pickle persistence, but exact byte compatibility must still be tested before approval

#### Alternative Disposition

| Alternative | Disposition |
| --- | --- |
| Upgrade RedisVL to 0.5.2 or later | Viable but rejected as non-minimal. It unlocks ml-dtypes >=0.5 while changing RedisVL semantic-cache, vectorizer, schema, filter and query behavior. Use only if the package-scoped runtime override proves incompatible |
| Package-scoped override in uv | Supported by uv 0.11.25+ for runtime dependency metadata. uv 0.11.26 can set `{ package = { name = "redisvl", version = "0.4.1" }, dependencies = ["ml-dtypes==0.5.4"] }`. It does not scope `build-system.requires`, so it cannot rewrite setuptools inside ml-dtypes 0.4.1. This exact runtime override is approved because RedisVL's 0.5.2 release explicitly widened the same requirement to `<1.0.0`, establishing upstream compatibility |
| Global build override/floor | Rejected. A constraint is additive and failed; a global override would disregard exact package metadata for every build and is broader than necessary |
| PyPI prebuilt wheel | Required for the selected package. Add `no-build-package = ["ml-dtypes"]` so uv fails closed if no compatible wheel exists. This prevents source-build setuptools from entering the builder |
| Immutable wheelhouse | Recommended follow-up for durable offline reproduction, but not required in this bounded correction because `uv.lock` retains exact wheel URLs/hashes and the selected CPython/platform wheels have PyPI PEP 740 provenance. If implemented, mirror byte-identical wheels only and bind an internal simple-index snapshot digest; never rebuild them |
| Delete `/root/.cache/uv` after build | Not the remediation. Deleting the full cache after a verified wheels-only install is approved defense-in-depth and reduces builder attack surface, but cache deletion alone cannot prove that no vulnerable executable participated in the build |

#### Exact Executable Remediation

Start at exact source `165a94ecfbf21d7ff4626815ac6b298ac34e2adb`. Change only root `pyproject.toml`, generated root `uv.lock`, and root `Dockerfile`. Preserve `litellm-rust/Cargo.lock` byte-for-byte

In root `[tool.uv]`, append these entries to the existing configuration. Do not add `build-constraint-dependencies`

```toml
override-dependencies = [
    "packaging>=24.0",
    "cryptography>=50.0.0,<51.0",
    { package = { name = "redisvl", version = "0.4.1" }, dependencies = ["ml-dtypes==0.5.4"] },
]
no-build-package = ["ml-dtypes"]
required-version = ">=0.11.26,<0.11.27"
```

Regenerate `uv.lock` with checksum-verified uv 0.11.26. Expected direct package delta is only `ml-dtypes 0.4.1` -> 0.5.4 plus override metadata and wheel records. RedisVL must remain 0.4.1, NumPy must remain on the existing resolution, and unrelated packages must not move. The lock must select the upstream PyPI wheels and hashes, never the sdist. For release `linux/amd64` and CPython 3.13, exact wheel is `ml_dtypes-0.5.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`, SHA-256 `533ce891ba774eabf607172254f2e7260ba5f57bdd64030c9a4fcfbd99815d0d`. Metadata SHA-256 is `51b5729b48ce71736748bbf43d4f355485f42b44977d6016717bbd6b11b7dfc0`

The arm64 wheel `ml_dtypes-0.5.4-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl`, SHA-256 `ce756d3a10d0c4067172804c9cc276ba9cc0ff47af9078ad439b075d1abdc29b`, is provenance/lock evidence only and authorizes no arm64 candidate. Retain all Python 3.10-3.14 x86_64/aarch64 wheel hashes emitted by `uv.lock` so the repository's declared Python range remains resolvable. The 0.5.4 CPython 3.10-3.14 Linux wheel hashes are recorded in Reopen 1 evidence

Verify the PyPI Integrity API PEP 740 attestation for the exact amd64 wheel. Require publisher kind GitHub, repository `jax-ml/ml_dtypes`, workflow `wheels.yml`, release environment, subject filename exactly equal to the wheel, and subject SHA-256 `533ce891...15d0d`. The release tag `v0.5.4` points through annotated tag object `882eb0f8d64a13696122945e4fb276e3cbf52ce8` to commit `9fd1a480f1cdb23b3d28dfea5eadf3d84b6dfc62`. Retain sanitized provenance verification and bundle checksum

Keep root Dockerfile's approved uv replacement exactly `ghcr.io/astral-sh/uv:0.11.26@sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`, requiring amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`. After the second frozen sync and all build outputs are complete, add one final builder-stage `RUN uv cache clean && test ! -d /root/.cache/uv/archive-v0 && test ! -d /root/.cache/uv/sdists-v9`. This cleanup is not counted as the vulnerability fix; it is accepted only after logs prove ml-dtypes installed from the attested wheel and no sdist/build environment was used

Every CI or local command that reads the new scoped override must run uv 0.11.26. The current repository default and workflows pin 0.10.9, which reject scoped override syntax. Implementation must therefore update root `required-version` and all repository-controlled `setup-uv-with-retries` caller pins from 0.10.9 to 0.11.26, or PMA must split that mechanical alignment into a prerequisite task. Do not land a lock/config unreadable by normal CI. `scripts/install.sh` and `scripts/install-cli.sh` also pin 0.10.9; update them only if they execute root project lock/sync behavior, otherwise record and leave them because changing installer product behavior is outside this remediation. This condition expands the implementation impact beyond the prior three-file boundary and requires PMA to approve the CI pin files before activation

#### Tests, Scans And Stop Gates

1. Require clean baseline fingerprints: `pyproject.toml` `a65b83b54f2ae160ac7ffa06119588ac79ff5b08f7eda89e901f60063ff63bbb`, `uv.lock` `2cbab3eb78c04cc8a8a7daa58550c7522071d9e39d2063917a52b79dc5635c12`, `Dockerfile` `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, and source commit above
2. Verify `uv 0.11.26`, run lock generation, `uv lock --check`, and all required frozen syncs with empty task-owned caches. Require `uv tree --invert --package ml-dtypes` to show RedisVL 0.4.1 -> ml-dtypes 0.5.4, no RedisVL version change, no sdist preparation, and installer output selecting the expected wheel hash
3. Run `make check`, `make lint`, the complete Redis semantic-cache test file, Valkey semantic-cache tests because it inherits Redis cache behavior, and real Redis/RediSearch sync+async semantic-cache store/check/TTL/filter/isolation/reconnect tests. Add a focused compatibility test proving 0.4.1 and 0.5.4 produce identical `bfloat16` bytes for representative finite, boundary, NaN and infinity vectors and that existing stored bfloat16 vectors round-trip under 0.5.4. Reject byte/index schema drift
4. Run the prior Rust and UI matrices unchanged even though Cargo is immutable. Build exact clean amd64 builder/final from committed defaults; assert uv 0.11.26 identity, ml-dtypes 0.5.4, RedisVL 0.4.1, NumPy unchanged, native imports, Prisma, migrations, normal entrypoint and all TASK-011 behavioral gates
5. Generate new SPDX and CycloneDX SBOMs and same-current-frozen-DB scans for selected uv input, exact builder and exact final. Raw builder evidence must contain ml-dtypes 0.5.4 and neither setuptools 68.1.2 nor any ml-dtypes sdist/build environment. It must contain quinn-proto >=0.11.15 and rustls-webpki >=0.103.13 in both uv/uvx. Zero Critical and zero fixable High remain mandatory, with independent disposition of all other/new Highs. No ignore/VEX/cache-path exclusion may suppress a real finding
6. Verify PyPI attestation and wheel SHA-256 before use, retain exact lock/diff/build inputs and artifact checksums, run secret scans and disposable cleanup, then follow the previously approved builder/final registry signing procedure only after PMA names the signer

Stop if uv lock moves RedisVL, NumPy or unrelated dependencies; any supported environment lacks a 0.5.4 wheel; PyPI provenance fails; uv builds ml-dtypes from sdist; bfloat16 bytes or stored-vector retrieval drift; Redis semantic cache behavior changes; the builder contains vulnerable setuptools; any Critical/fixable High exists; Cargo changes; CI remains pinned to incompatible uv; or any production/registry/deployment boundary is crossed

#### Rollback

Before commit/publication, revert exactly root `pyproject.toml`, generated `uv.lock`, root `Dockerfile`, and any PMA-approved uv-version pin files to baseline fingerprints, then destroy all task builders, caches and images. Never keep the uv image bump while restoring a lock generated by incompatible uv, and never treat cache deletion as a security fix

After a separately approved deployment, restore the exact pre-deployment Fedora digest and prior source revision; rerun readiness, migrations, model inventory, Responses, MCP/LazyMCP, real tool, Redis semantic cache, image/config identity and logs. The dependency change has no schema migration, but Redis index/vector byte compatibility must pass before deployment. NAS remains untouched

#### Reopen 1 Acceptance Criteria Coverage

- **AC-1: PASS.** Current and upstream RedisVL/ml-dtypes dependency metadata, release histories, wheel availability, hashes, provenance and behavior surface are mapped
- **AC-2: PASS.** One exact executable correction is selected: scoped RedisVL 0.4.1 runtime override to ml-dtypes 0.5.4, wheels-only enforcement, uv 0.11.26 and defense-in-depth cache cleanup. No setuptools override or Cargo edit is allowed
- **AC-3: PASS.** Exact files, versions, digests, provenance, CI uv compatibility, tests, SBOM/scans, stop gates and rollback are defined
- **AC-4: PASS UNCHANGED.** Existing private-registry signing policy remains valid and fail-closed; signer identity is still required before execution
- **AC-5: PASS.** Original task and evidence record Reopen 1 and signed implementation-ready handoff. No source, lock, build, push, sign, registry, host, production or deployment mutation occurred

#### Reopen 1 Documentation Impact

No product documentation change is required. If a repository wheelhouse becomes maintained release infrastructure, route a separate architecture task documenting index layout, immutable snapshot digest, publisher provenance, refresh/retention and CodeMap ownership. This task update is the bounded dependency/release design source

#### Reopen 1 Open Risks

- The selected scoped override requires uv 0.11.25+ while repository CI and local defaults currently pin 0.10.9. PMA must authorize version-pin alignment or choose the more invasive RedisVL 0.5.2 package upgrade
- RedisVL 0.5.2 is upstream proof that ml-dtypes <1 is supported, but RedisVL 0.4.1 was not released with that widened bound. Focused and real Redis semantic-cache compatibility tests remain mandatory
- ml-dtypes 0.5.3 changed pickle compatibility. LiteLLM's reviewed RedisVL path stores vector bytes rather than pickled ml-dtypes values, but byte-level and existing-index regressions must prove safety
- The selected wheel uses manylinux 2.27/2.28 rather than 2.17. The Wolfi glibc 2.44 amd64 builder exceeds that floor, but copied ELF dependency and ABI checks remain mandatory
- Signing remains blocked until PMA names an approved release identity

#### Reopen 1 Recommended Next Step

PMA should approve the scoped dependency override and CI uv 0.11.26 pin alignment, then reopen TASK-004 with the exact contract above. If PMA rejects CI pin expansion, the fallback is a separately reviewed RedisVL 0.5.2 plus ml-dtypes 0.5.4 upgrade with its larger semantic-cache regression scope. Do not retry the impossible global build constraint

#### Reopen 1 Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS Reopen 1 investigation. Replace the impossible global setuptools floor with a uv 0.11.26 package-scoped override of RedisVL 0.4.1's ml-dtypes requirement to exact 0.5.4, enforce `no-build-package = ["ml-dtypes"]`, regenerate the lock, and install only the PEP 740-attested CPython 3.13 amd64 wheel SHA-256 `533ce891ba774eabf607172254f2e7260ba5f57bdd64030c9a4fcfbd99815d0d`. Keep RedisVL 0.4.1, NumPy, application Cargo, product code and all other dependencies unchanged. Retain approved uv 0.11.26 OCI index `sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5` and amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`; clean the builder uv cache only after proving wheels-only installation. PMA must approve alignment of repository CI uv pins from 0.10.9 to 0.11.26 because older uv cannot parse the scoped override. Reject dependency drift, sdist/build use, bfloat16/index incompatibility, provenance failure, any fixable High/Critical, Cargo change, signing without an approved identity, or any publication/deployment/host mutation
