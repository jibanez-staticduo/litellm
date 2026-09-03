# TASK-2026-09-03-002 Evidence Summary

## Summary

REJECT Fedora deployment. The exact Reopen 6 source, builder, final image, security artifacts, functional qualification, cleanup, current fork main, and current Fedora baseline are coherent. Release cannot proceed because no approved StaticDuo signer exists, no immutable registry manifest/config/signature/attestation chain exists, current-Fedora upgrade and prior-image compatibility across ten new migrations are unproved, and no fresh protected DB backup/restore unit exists

## Work Performed

- Verified local and remote fork main at `445877a1243b10af2457a2f363cc54d6b31208a9`; qualified source `bf58974a935521fa570fa7e280c51a00b2e5b54e` is its direct parent and later changes affect StaticEng evidence only
- Verified retained amd64 builder `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` carry the exact source/task labels
- Recomputed all 21 Reopen 6 evidence checksums and parsed all four machine-readable Grype scans; builder and final each have zero Critical and zero High under the frozen database
- Rechecked cleanup: zero task containers, networks, volumes, builders, and worktrees remain; both exact release images remain available locally
- Traced `cosign.pub` to unchanged upstream BerriAI provenance, checked non-secret local/repository signer metadata, and found no approved StaticDuo signer or executable Cosign installation
- Captured current Fedora identity, health, dependencies, protected hashes/modes, Compose rendering, model/fallback fingerprints, MCP status counts, backup-tool capability, rollback-image availability, and release-artifact inventory through read-only secret-safe probes
- Compared current Fedora source with the candidate and identified ten new migrations; reviewed evidence and found only empty-database/idempotent migration testing, not the required current-schema upgrade and prior-image compatibility test
- Ran `staticeng_validate`; result PASS with zero warnings

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact source, retained images, labels, qualification artifacts, security scan results, cleanup, and production preservation are verified
- **AC-2: FAIL.** Signing/attestation is mandatory and no approved executable StaticDuo signer is available
- **AC-3: FAIL.** Publication and rollback contracts are frozen, but registry manifests/config linkage/signatures/attestations, migration rollback compatibility, and a fresh DB backup/restore unit do not yet exist
- **AC-4: PASS FOR DEFINITION.** Full Fedora gates and 900-second soak are frozen in the task; execution remains prohibited
- **AC-5: PASS.** Signed verdict is REJECT and all work was read-only/secret-safe with no production, registry, image, container, DB, config, or NAS mutation

## Exact Identities

```text
fork main: 445877a1243b10af2457a2f363cc54d6b31208a9
qualified source: bf58974a935521fa570fa7e280c51a00b2e5b54e
qualified source tree: 5bb1b3185d25ba851482ee022503178996df3341
qualified builder config: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
qualified final config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
Fedora rollback selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
Fedora rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
repository cosign.pub SHA-256: ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3
```

## Documentation Impact

Product and CodeMap documentation are not required. This investigation changes no product behavior or maintained source structure

## Open Risks

- No approved fork release signer or verification identity
- No registry manifest/config/signature/attestation chain
- Ten candidate migrations lack current-Fedora upgrade and prior-image compatibility evidence
- No fresh owner-only DB dump/list/checksum/restore rehearsal
- Deployment behavior and 15-minute production soak remain unexecuted

## Recommended Next Step

PMA should route signer approval and isolated current-schema upgrade/prior-image compatibility as blocking prerequisites. After both pass, request Tech Lead reauthorization and activate TASK-012 for exact publication, fresh backup, Fedora-only digest deployment, complete post-deploy gates, and 900-second soak. NAS and stable remain untouched

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT FEDORA DEPLOYMENT. Qualification passes for the exact retained source and images, and current Fedora is stable with a usable immutable rollback selector. Missing approved StaticDuo signing identity, absent registry digest/signature/attestation chain, unproved current-schema upgrade and prior-image compatibility, and absent fresh verified DB backup block release. Keep TASK-012, publication, signing, Fedora, stable, and NAS blocked until those prerequisites pass and Tech Lead reauthorizes. No mutation occurred

## Reopen 1

### Summary

AUTHORIZE TASK-012 for Fedora-only release under the exact fail-closed handoff in the task. TASK-003 closes isolated current-schema upgrade and rollback-image startup. TASK-004 closes immutable registry publication, approved signing, all six attestations, exact source/config binding, and persistence. Current `main` differs from qualified source only by StaticEng evidence, and Fedora remains unchanged and healthy on its exact rollback selector

### Work Performed

- Rechecked exact registry manifests, configs, amd64 platform, source/task labels, and unique quarantine-tag resolution directly from the private registry
- Recomputed public-key and predicate checksums; verified qualification SBOM byte equality and SLSA source/tree/config/scan/database binding
- Downloaded checksum-pinned Cosign 3.1.3 to a disposable path, freshly verified both signatures plus all six attestations and transparency-log inclusion, then removed the verifier
- Reviewed TASK-003's secret-free Fedora 151-to-161 migration execution, two idempotent candidate restarts, rollback-image startup against upgraded schema, cleanup, and production preservation
- Verified `main == origin/main == 761742b1c98e68502e7b638bb61d8a0a5e93c4bc`, qualified and frozen-upstream ancestry, and zero non-StaticEng changes after qualified source
- Recaptured Fedora selector/config/source, health, readiness/liveliness, dependency identities, protected hashes/modes, Compose rendering, model/fallback fingerprints, qualified alias topology, and MCP status counts through read-only secret-safe probes
- Froze exact TASK-012 backup/restore, deploy-only-LiteLLM, post-deploy, log, 900-second soak, and rollback handoff; no deployment or host mutation occurred

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact qualified source, builder/final local and registry identities, qualification, scans, cleanup, ancestry, and evidence-only main delta pass
- **AC-2: PASS.** PMA-approved StaticDuo signer and all required signatures/attestations verify independently against exact digest/source/predicate identities
- **AC-3: PASS FOR AUTHORIZATION.** Registry manifest/config chain, prior Fedora digest/config, and migration compatibility are exact. Fresh production backup/list/checksum/isolated restore remains mandatory before TASK-012 selector mutation
- **AC-4: PASS.** Exact Fedora post-deploy gates, 900-second soak, minute-15 repeat, and verified rollback are frozen in the task
- **AC-5: PASS.** TASK-012 is authorized for the exact Fedora-only selector and conditions; this review made no runtime or registry mutation

### Exact Release Identity

```text
main/origin-main: 761742b1c98e68502e7b638bb61d8a0a5e93c4bc
source: bf58974a935521fa570fa7e280c51a00b2e5b54e
builder: docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa
builder config: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
release selector: docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
release config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
current Fedora rollback selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
current Fedora rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
signer: staticduo-litellm-release-self-managed-v1
public key SPKI SHA-256: 2b3b91453b283be502c0cd035d835d5b58faa42b1f638297c45da75b09a15e71
```

### Documentation Impact

No product, architecture, technical, or CodeMap update is required because review and prerequisite release operations change no maintained product behavior or source structure

### Open Risks

- Fresh production backup/checksum/list/isolated restore verification must pass before selector mutation
- The signing identity is self-managed rather than hardware-backed
- Full production behavior, logs, 15-minute soak, and any required rollback remain TASK-012 execution gates

### Recommended Next Step

PMA may activate TASK-012 with the exact authorization in the task. Keep NAS and mutable tags untouched

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

AUTHORIZE TASK-012 FEDORA-ONLY RELEASE. Deploy only `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, requiring config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. Before mutation, complete the fresh protected Fedora baseline and custom-format DB backup/checksum/list plus isolated restore verification. Change only `LITELLM_IMAGE`, recreate only `litellm` with `--no-deps`, run complete identity/migration/health/models/Responses/MCP/LazyMCP/audience/real-tool/log gates and a continuous 900-second soak, and roll back immediately to the freshly captured prior digest on any failure. Do not move tags, restore production DB automatically, or touch NAS. No mutation occurred in this review
