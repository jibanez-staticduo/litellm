---
id: TASK-2026-09-03-002-review-fedora-release-readiness
complexity: complex
track: investigation
slice: qa
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: Review Fedora release readiness

## Objective

Review exact qualified images/evidence, current fork main, publication/signing options, Fedora baseline/rollback, and authorize or reject Fedora deployment.

## Acceptance Criteria

- [ ] AC-1: Verify exact source, builder/final identities, full qualification and cleanup evidence.
- [ ] AC-2: Resolve whether signing/attestation is mandatory before Fedora canary and identify an approved executable signer or explicit policy disposition.
- [ ] AC-3: Freeze unique immutable registry publication, manifest/config identity chain, and rollback selector/DB backup.
- [ ] AC-4: Freeze Fedora health/models/Responses/MCP/LazyMCP/real-tool/log/15-minute observation gates.
- [ ] AC-5: Return signed authorize/reject verdict; no mutation.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review TASK-011 Reopen 6 and current exact fork main. Inspect existing repository cosign.pub and available approved signing identities without exposing secrets. Decide signing requirement for Fedora canary. Read current Fedora state and release runbook only through secret-safe commands. No publish/sign/config/DB/container/deploy mutation. If authorized, provide exact immutable publication and rollback/deploy handoff; otherwise exact blocker.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Findings

1. **BLOCKER: no approved release signer is available.** The governing SCR requires signatures and attestations before Fedora release. Repository `cosign.pub` has file SHA-256 `ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3`, but it is the unchanged upstream BerriAI release key introduced by upstream commit `0112e53046018d726492c814b3644b7d376029d0`, not an approved StaticDuo release identity. The local host has no Cosign binary, signer environment name, alternate key file, KMS URI, or frozen keyless workflow identity. The fork repository exposes no Actions secret, variable, or environment names that identify an approved signer. Git SSH commit-signing identity does not authorize image signing. Signing and all six required attestations therefore remain mandatory and impossible to execute under current approval
2. **BLOCKER: the qualified images have no registry manifest/config publication chain.** TASK-011 Reopen 6 retained exact local amd64 builder config ID `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final config ID `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`, both from source `bf58974a935521fa570fa7e280c51a00b2e5b54e`, but no registry digest exists. Exact registry manifests, config equality, signatures, SPDX/CycloneDX/SLSA subjects, referrer discoverability, and fresh verification cannot yet be frozen. Publication identities reserved for execution are unique quarantine tags `docker.staticduo.com/litellm:quarantine-task011-r6-builder-bf58974a9355-eb673f1c4f02` and `docker.staticduo.com/litellm:quarantine-task011-r6-final-bf58974a9355-ad33017b518b`; both were unresolved at review time. Tags are publication handles only. Deployment may use only the resolved final digest
3. **BLOCKER: required migration upgrade and prior-image rollback compatibility are not evidenced.** Current Fedora runs source revision `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`, while the qualified source adds ten proxy-extras migrations. TASK-010 and TASK-011 prove 161 migrations against an empty database and idempotent restart, but neither proves upgrade from an approved current-Fedora schema fixture nor that the prior digest starts safely after those migrations. This violates the SCR's explicit pre-deploy migration gate. At least two new migrations execute `UPDATE`, and rollback cannot be assumed from additive schema inspection
4. **BLOCKER: no current protected DB backup/restore artifact exists.** Fedora has no database dump under its release hierarchy. A secret-safe dry run confirms `pg_dump` can read the current database and `pg_restore` is available, so the required owner-only backup, listing, checksum, and restore rehearsal are feasible only in the later authorized release task. Deployment remains prohibited until that task creates and verifies the fresh rollback unit before selector mutation
5. **PASS: exact source, retained image, security, cleanup, and present Fedora baseline are coherent.** `origin/main` and local `main` are exact `445877a1243b10af2457a2f363cc54d6b31208a9`; the qualified source is its direct parent, and all later changes are StaticEng evidence only. Dockerfile, project, lock, application, migration, UI, and Rust inputs are unchanged from the qualified source. All 21 Reopen 6 artifacts match their SHA-256 manifest. Frozen Grype 0.118.0 DB schema 6.1.9 built `2026-09-03T06:30:55Z` reports builder/final zero Critical and zero High. Live image metadata matches evidence, cleanup counts are zero for task containers/networks/volumes/builders/worktrees, and only the two qualified images remain
6. **PASS: Fedora is presently stable and matches the frozen operational baseline.** It runs immutable selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, local image/config ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, OCI revision `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`, amd64, healthy, restart 0, OOM false, readiness/liveliness 200. Its model projection remains 26 rows at `98f0d541823b9f7c19c0a19d338e2f9027b07b6801015d2aeb5ab739229e6231`; 24 fallback rules remain at `a057787927e9cfb8f5b140f7b4ed7e7f90f792e88fdc86b84d0ffdb7cf2c0f0c`; MCP remains 13 registrations with 11 healthy, one auth-required, and one unknown. Protected file hashes match the 2026-09-01 baseline, dependencies are healthy, and the current rollback image is locally inspectable

### Frozen Release And Rollback Handoff

After PMA names an approved StaticDuo signer and the migration compatibility blocker is independently cleared, TASK-012 may publish without rebuilding. The release operator must first verify local builder/final IDs and source labels exactly as above, then push each retained image once to its reserved unique quarantine tag. Immediately resolve each tag to a registry manifest digest, require the manifest's `.config.digest` to equal its respective retained local ID, and freeze:

```text
BUILDER_REF=docker.staticduo.com/litellm@sha256:<resolved-builder-manifest>
BUILDER_CONFIG=sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
RELEASE_REF=docker.staticduo.com/litellm@sha256:<resolved-final-manifest>
RELEASE_CONFIG=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
SOURCE_REVISION=bf58974a935521fa570fa7e280c51a00b2e5b54e
```

Sign both digest references with the newly named approved identity. Attach and freshly verify SPDX JSON, CycloneDX JSON, and SLSA provenance v1 attestations for both. Require exact task/revision annotations, sole manifest subject, predicate types and content, public identity/fingerprint, registry persistence, and `cosign tree` visibility. Never sign local config IDs or deploy by tag. Do not move `stable`

Immediately before Fedora mutation, rerun the secret-safe baseline and create a fresh `0700` attempt directory with `0600` rollback files. Capture `.env`, Compose, config, wrappers, exact prior digest/config/source, dependency IDs/start times, health, restart/OOM, model/fallback hashes, MCP status counts, Responses/LazyMCP/real-tool and bounded-log baseline. Create a custom-format DB dump, list it, checksum it, and complete the approved restore rehearsal without writing production. The authoritative `PREVIOUS_REF` is the fresh current selector, expected at review time to be `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`; stop if it differs until the new baseline is reviewed

Render Compose with `RELEASE_REF` and prove only `litellm` image changes. Atomically change the single `LITELLM_IMAGE` line, pull the digest, and run only `docker compose ... up -d --no-deps litellm`. Require within 180 seconds exact digest/config/source, healthy, readiness/liveliness 200, restart 0, OOM false, unchanged dependencies/config/topology, exact pre/post inventory hashes, successful migration state, one real Responses request, MCP REST, all LazyMCP discovery/challenge/audience/initialize gates, and `defend_memory` / `defend_memory-find` success without payload retention. Review only bounded post-start sanitized log classes

Observe continuously for at least 900 seconds with 30-second polls. Every poll must preserve container/start identity, release manifest/config, health, readiness/liveliness, restart 0, OOM false, and dependency identities. At minute 15 rerun inventory, Responses, MCP REST, all LazyMCP discovery/challenge/authorized real-tool gates, preservation hashes, migration status, and bounded log review. Any failed, shortened, or ambiguous gate triggers immediate rollback: restore only the fresh `PREVIOUS_REF`, recreate only `litellm` with `--no-deps`, and verify prior digest/config plus full health, inventory, Responses, MCP/LazyMCP/real-tool, migration compatibility, dependencies, and logs. Never restore the DB automatically or touch NAS

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact source, direct-parent fork main, retained builder/final IDs, qualification matrix, artifact checksums, zero Critical/High scans, live labels, cleanup, and production preservation were independently verified
- **AC-2: FAIL.** Signing is mandatory under the approved SCR, but no PMA-approved StaticDuo private-key/KMS identity or frozen keyless workflow exists. The repository key is upstream BerriAI's trust root and cannot be repurposed by inference
- **AC-3: FAIL.** Unique publication tags and the required digest/config chain are frozen as an execution contract, and the current digest rollback selector is known, but no registry manifests/signatures/attestations or fresh DB backup/restore rehearsal exist. Prior-image migration compatibility is also unproved
- **AC-4: PASS FOR DEFINITION, NOT EXECUTION.** Exact health, models/fallbacks, Responses, MCP/LazyMCP/authorized real-tool, preservation, sanitized logs, 30-second polling, 900-second soak, minute-15 repeat, and rollback gates are frozen. No deploy or soak was authorized or performed
- **AC-5: PASS.** Verdict is explicit REJECT. Review used read-only and secret-safe repository, registry-name, Docker metadata, GitHub metadata, and Fedora probes. No image push/sign, registry mutation, selector/config/DB mutation, container restart/recreation, deployment, or NAS action occurred

### Documentation Impact

Product and CodeMap documentation are not required because this investigation changes no product behavior, architecture, source, route, schema, or maintained tooling. The governing SCR and task evidence remain the release sources of truth

### Open Risks

- An authorized release identity and its exact verification policy remain unresolved
- Ten migrations separate current Fedora from the candidate, including data-update statements; safe prior-image startup after upgrade is not established
- Registry manifest/config equality, signature/attestation persistence, and final digest do not exist until authorized publication
- The fresh DB backup, restore rehearsal, current functional baseline, deployment, rollback readiness, and 15-minute soak remain execution-time gates

### Recommended Next Step

PMA must keep TASK-012 blocked. First obtain explicit security-owner approval for one executable StaticDuo signer and public verification identity. In parallel, route a narrowly scoped isolated migration task that upgrades a secret-safe current-Fedora schema fixture with the exact final image and proves the current rollback image can start against the upgraded schema. After both signed PASS results, reopen this task or request Tech Lead reauthorization. Then activate TASK-012 to publish and verify the frozen builder/final chain, create the fresh Fedora rollback unit and DB backup, deploy only Fedora by final digest, execute all gates and the full 15-minute soak, and leave NAS untouched

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT FEDORA DEPLOYMENT. Exact source `bf58974a935521fa570fa7e280c51a00b2e5b54e`, builder `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac`, and final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` pass qualification, checksum, zero-Critical/High, retention, and cleanup review, and current Fedora is stable on rollback selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`. Release remains blocked because the SCR mandates builder/final signing and SPDX/CycloneDX/SLSA attestations but no approved StaticDuo signer exists; the tracked `cosign.pub` is upstream BerriAI's key, not authority to sign this fork. No registry manifest/config chain exists, ten migrations lack current-Fedora upgrade and prior-image compatibility evidence, and no fresh verified DB backup/restore unit exists. Keep TASK-012, publication, signing, Fedora, stable, and NAS blocked. Route signer approval plus isolated current-schema upgrade/rollback compatibility, then return for Tech Lead reauthorization. No mutation occurred

## Reopen History

### Reopen 1 - Schema and signed publication prerequisites complete

[Agent Message] From: product_manager To: tech_lead

Reopen Fedora readiness after TASK-003 schema/rollback PASS and TASK-004 signing/attestation PASS. Verify exact final registry digest/config identity, signatures/attestations/source binding, current main evidence-only delta, Fedora current baseline and exact release runbook. If all prerequisites now pass, authorize TASK-012 with exact publication selector, fresh protected backup/restore verification, deploy-only-litellm, complete health/models/Responses/MCP/LazyMCP/real-tool/log gates and 15-minute soak/rollback. Update review evidence/task. Do not deploy or mutate Fedora/NAS in this review.

### Reopen 1 Findings

No blocking findings remain for activating TASK-012. The previous signer, registry-chain, and isolated schema/rollback blockers are closed. Fresh protected production backup/restore verification, deployment behavior, post-deploy gates, and the 15-minute soak remain mandatory execution-time gates inside TASK-012, not completed review claims

1. **PASS: immutable signed release identity is exact and independently reverified.** Builder reference `docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa` resolves to qualified config `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac`. Final release selector `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` resolves to qualified config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`. Both are single `linux/amd64` manifests labelled with source `bf58974a935521fa570fa7e280c51a00b2e5b54e` and task `TASK-2026-09-01-011-r6`. Their unique quarantine tags still resolve to these exact manifests
2. **PASS: StaticDuo signatures, attestations, and source binding verify fresh.** Dedicated PMA-approved signer `staticduo-litellm-release-self-managed-v1` has retained public-key file SHA-256 `3983a067c0f99ec9e44e91b58f0991e6a065c74a11c6e70095abe178904005ec` and SPKI SHA-256 `2b3b91453b283be502c0cd035d835d5b58faa42b1f638297c45da75b09a15e71`. Independently downloaded checksum-pinned Cosign 3.1.3 verified each digest's image signature with exact task/revision annotations and its SPDX, CycloneDX, and SLSA provenance v1 attestations, including transparency-log inclusion. Predicate checksums pass; SPDX/CycloneDX predicates are byte-identical to Reopen 6 qualification artifacts; SLSA predicates bind the exact source/tree, target, empty build arguments, platform, BuildKit, config IDs, SBOMs, scans, and frozen vulnerability database
3. **PASS: migration upgrade and rollback-image startup are independently qualified.** TASK-003 restored secret-free Fedora schema plus its 151-row migration ledger into isolated PostgreSQL, applied the candidate's exact ten pending migrations to 161 with two healthy idempotent candidate restarts, then started current Fedora rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` healthy against the upgraded clone without schema or ledger mutation. Cleanup and unchanged Fedora production were proven. The fixture contains no application rows, so production backup remains compulsory before deployment
4. **PASS: fork main remains source-equivalent to qualification.** Local and remote `main` are exact `761742b1c98e68502e7b638bb61d8a0a5e93c4bc`. Qualified source `bf58974a935521fa570fa7e280c51a00b2e5b54e` and frozen upstream `10631eb834c7802aa61611e807474170b8a4d425` are ancestors. Every later path is under `.staticeng/`; no source, build, lock, migration, runtime, UI, Rust, test, or deployment input changed
5. **PASS: Fedora remains at the approved fresh baseline.** Fedora still runs selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, config ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, source `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`, healthy, restart 0, OOM false, readiness/liveliness 200. Model projection is still 26 rows at `98f0d541823b9f7c19c0a19d338e2f9027b07b6801015d2aeb5ab739229e6231`; fallback projection remains 24 rules at `a057787927e9cfb8f5b140f7b4ed7e7f90f792e88fdc86b84d0ffdb7cf2c0f0c`; qualified aliases remain 6/6; MCP remains 13 registrations with 11 healthy, one auth-required, and one unknown. Protected hashes and dependency identities remain unchanged. The exact release image is not pulled locally, which is correct before TASK-012
6. **PASS: exact release and rollback procedure is frozen and fail-closed.** TASK-012 may now perform the fresh backup and Fedora-only deployment contract below. Any preflight, identity, backup, restore, migration, behavior, log, soak, or rollback uncertainty revokes authorization before further mutation

### Reopen 1 Authorized TASK-012 Handoff

TASK-012 is authorized only for exact final selector:

```text
RELEASE_REF=docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
RELEASE_CONFIG=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
SOURCE_REVISION=bf58974a935521fa570fa7e280c51a00b2e5b54e
EXPECTED_PREVIOUS_REF=docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
EXPECTED_PREVIOUS_CONFIG=sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
STACK=/home/staticduo/docker/litellm
```

Before any selector change, TASK-012 must freshly verify `origin/main == 761742b1c98e68502e7b638bb61d8a0a5e93c4bc`, no non-StaticEng delta after qualified source, the release manifest/config/source/platform, the public-key fingerprints, image signature, all three attestation types, exact sole subjects and predicate checksums. Stop if the current Fedora selector/config differs from `EXPECTED_PREVIOUS_REF`/`EXPECTED_PREVIOUS_CONFIG`, any protected baseline differs, or any unrelated service/dependency changed

Create a new host-local attempt with directories mode `0700` and files mode `0600`. Capture the current `.env`, Compose, config, wrappers, prior selector/image inspection, dependency identities/start times, mounts/networks/runtime projection, protected hashes, credential metadata, migration ledger, exact model/fallback and MCP fingerprints, one baseline Responses result, all required MCP/LazyMCP discovery/challenge/authorized initialize/real-tool results, and bounded log start timestamp without payloads or secrets. Stream a current custom-format production DB dump into the protected rollback unit, generate a restore listing, verify its checksum, and restore it into a disposable isolated PostgreSQL instance. Require successful restore, expected migration-ledger/schema state, no task artifact leakage, and cleanup of the restore instance. No production DB write or automatic restore is authorized

Pull only `RELEASE_REF`, then prove local image ID equals `RELEASE_CONFIG`, amd64 and source label exact. Render Compose with the new selector and prove the only semantic change is `litellm` image. Atomically replace the single `LITELLM_IMAGE` line while preserving owner/mode and every other normalized byte. Recreate only Fedora `litellm` with `docker compose ... up -d --no-deps litellm`; do not invoke the broad release helper, move tags, recreate dependencies, edit configuration, or touch NAS

Within 180 seconds require running/healthy, readiness/liveliness 200, restart 0, OOM false, `.Config.Image == RELEASE_REF`, `.Image == RELEASE_CONFIG`, exact source revision, 161 successful migrations with no failure/rollback/log state, unchanged dependency IDs/start times, and exact equality for model/fallback/MCP/protected/config/credential/mount/network/port/ulimit/command projections. Run one authorized real Responses request, MCP REST and `/mcp`, all six LazyMCP discovery aliases, aggregate/scoped/toolset exact challenges and audience rejection, authorized initialize/list/call, and `defend_memory` / `defend_memory-find`; retain only safe status/classification metadata

Review only bounded logs since the captured timestamp. Any new traceback, 5xx, migration/schema failure, auth/audience/permission regression, unexpected 401/403, discovery 404, OAuth/token error, MCP/tool failure, response failure, credential forwarding or leakage indicator, device-auth prompt, restart, OOM, or unexplained error burst fails release

Observe continuously for at least 900 seconds, polling every 30 seconds for identical new container ID/start time, exact manifest/config/source, healthy state, readiness/liveliness 200, restart 0, OOM false, and unchanged dependency identities. At minute 15 rerun migration state, inventory, Responses, MCP REST, all LazyMCP discovery/challenge/audience/authorized real-tool gates, preservation hashes, and bounded log review. A shortened or partial soak is failure

On any failure after selector mutation, immediately restore only the fresh protected `PREVIOUS_REF`, preserve `.env` owner/mode/non-image content, pull it if needed, and recreate only `litellm` with `--no-deps`. Verify exact prior config/source, healthy/readiness/liveliness, restart 0, OOM false, migration compatibility, baseline model/fallback/MCP fingerprints, Responses, all LazyMCP gates, authorized real tool, dependencies, protected state, and logs. Do not restore the DB automatically, move tags, repair data/config ad hoc, or touch NAS. If rollback cannot be fully verified, stop and escalate a critical Fedora release incident to PMA

### Reopen 1 Acceptance Criteria Coverage

- **AC-1: PASS.** Exact qualified source, builder/final local and registry identities, complete functional/security evidence, cleanup, source ancestry, and evidence-only main delta are verified
- **AC-2: PASS.** Mandatory signing and attestations are fulfilled by the PMA-approved dedicated StaticDuo signer; fresh independent cryptographic, transparency, annotation, type, subject, source, content, and persistence checks pass
- **AC-3: PASS FOR RELEASE AUTHORIZATION.** Unique builder/final manifests and config chain are frozen, current rollback selector/config is exact, and isolated migration compatibility passes. Fresh production DB backup/checksum/list/restore verification remains a mandatory TASK-012 pre-mutation gate
- **AC-4: PASS.** Fedora baseline plus exact health, migration, model/fallback, Responses, MCP/LazyMCP/audience/real-tool, preservation, log, 30-second polling, 900-second soak, minute-15 repeat, and rollback gates are frozen
- **AC-5: PASS.** Verdict is AUTHORIZE TASK-012 under the exact fail-closed handoff. This review performed no image pull/push/sign, registry mutation, Fedora/NAS configuration or database mutation, container recreation/restart, deployment, or tag movement

### Reopen 1 Documentation Impact

No product, architecture, technical, or CodeMap update is required. The governing SCR, prerequisite evidence, this authorization, and TASK-012 execution evidence are the release sources of truth

### Reopen 1 Open Risks

- The signing key is self-managed rather than hardware-backed; rotation, backup, recovery, and access control remain release-owner responsibilities
- TASK-003's fixture had no application rows, so exact fresh production backup and isolated restore verification are non-waivable before deployment
- The rollback image passed upgraded-schema startup, but complete post-rollback functional behavior remains an execution-time gate if rollback occurs
- Registry consumers require Cosign 3.x or OCI-referrer-aware verification

### Reopen 1 Recommended Next Step

PMA may activate TASK-012 with this exact selector and handoff. TASK-012 must stop before mutation if any fresh identity, baseline, backup/restore, or rendering gate differs. If deployment occurs, complete every post-deploy gate and the full 15-minute Fedora soak before declaring PASS. NAS and mutable tags remain out of scope

### Reopen 1 Signed Handoff

[Agent Message] From: tech_lead To: product_manager

AUTHORIZE TASK-012 FEDORA-ONLY RELEASE. Deploy only `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, requiring config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. Exact qualification, zero-Critical/High scans, schema upgrade/rollback startup, registry config equality, StaticDuo signature, SPDX/CycloneDX/SLSA attestations, source binding, and evidence-only current-main delta pass independent review. Before selector mutation, require the full fresh protected Fedora baseline and custom-format DB backup/checksum/list plus isolated restore verification. Then change only the single `LITELLM_IMAGE` selector and recreate only `litellm` with `--no-deps`. Require exact image/source/migration identity, health, unchanged models/fallbacks/dependencies/configuration, Responses, MCP/LazyMCP/audience/authorized `defend_memory-find`, clean bounded logs, and a continuous 900-second soak with full minute-15 rerun. Any failure triggers exact prior-digest rollback and full verification. Do not move mutable tags, restore the DB automatically, or touch NAS. This review performed no deployment or host mutation
