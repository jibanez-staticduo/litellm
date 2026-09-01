---
id: TASK-2026-08-31-012-pin-venv-system-python
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: product_manager
handoff_from: tech_lead
reopened_count: 0
---

# Task: Pin venv to system Python 3.13

## Objective

Review and implement the smallest Dockerfile-only correction ensuring uv builds `/app/.venv` with pinned `/usr/bin/python3.13` and final validation uses that venv interpreter.

## Acceptance Criteria

- [ ] AC-1: Tech Lead approves/rejects TASK-011's exact three substitutions and portability assumptions.
- [ ] AC-2: Root Dockerfile alone changes both uv selectors to `/usr/bin/python3.13` and Prisma validation to `/app/.venv/bin/python`.
- [ ] AC-3: Python/venv ABI, Prisma, uvloop, Rust bridge, normal entrypoint, and runtime PATH behavior are verified without changing runtime ENV/entrypoints.
- [ ] AC-4: Locks, Cargo files, application source/tests, other Dockerfiles, production, and deployment remain unchanged.
- [ ] AC-5: New fingerprints/manifest/combined patch are independently reviewed before TASK-006 resumes.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review TASK-011's governed recommendation, Reopen 2 logs, and current Dockerfile. Do not edit implementation. Approve/reject only the exact three substitutions and define Developer evidence plus candidate re-freeze requirements.

## Implementation Handoff

[Agent Message] From: product_manager To: developer

Implement only the exact three Tech Lead-approved root Dockerfile substitutions recorded in this task. Do not change runtime PATH/ENV/entrypoints, locks, Cargo, source/tests, other Dockerfiles, deployment, production, or arm64 scope. Produce complete evidence and replacement eight-path fingerprints/manifest/combined patch; do not resume full TASK-006 build until independent review.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Findings And Authorization

[Agent Message] From: tech_lead To: product_manager

Verdict: APPROVE for bounded Developer implementation. Approve exactly TASK-011's three root-`Dockerfile` substitutions: replace both existing `--python python3.13` selectors with `--python /usr/bin/python3.13`, and replace only the final Prisma assertion's `python -c` with `/app/.venv/bin/python -c`. No other implementation change is authorized

The exact Reopen 2 raw build log independently confirms the linked failure. The pinned APK transaction installed system CPython `3.13.15-r4`, but the first `uv sync --python python3.13` downloaded managed `cpython-3.13.13-linux-x86_64-gnu`, selected CPython 3.13.13, and created `.venv` from it. Prisma was later generated under `/app/.venv/lib/python3.13/site-packages/prisma`. After only `/app/.venv` was copied into the runtime stage, the final bare `python` invocation reached an interpreter that could not import that package and failed with `ModuleNotFoundError`. No final image was emitted

The summarized Reopen 2 statement that `/app/.venv/bin` was not selected is imprecise. The current runtime `ENV` already places `/app/.venv/bin` first. The stronger raw evidence shows that the copied venv was based on uv's managed builder interpreter rather than the identically pinned builder/runtime system interpreter. A copied venv whose executable target is unavailable in the runtime cannot satisfy the contract; shell lookup may then continue to the system interpreter. The correction must therefore establish venv provenance with the two absolute selectors before making the final assertion fail closed through the explicit venv path

### Exact Three Substitutions

Apply the first substitution independently to both existing sync commands at current `Dockerfile:94` and `Dockerfile:115`:

```diff
-    --python python3.13
+    --python /usr/bin/python3.13
```

Apply the third substitution only to the interpreter token in the final assertion at current `Dockerfile:164`:

```diff
-    python -c "from prisma.client import BINARY_PATHS; paths = list(BINARY_PATHS.query_engine.values()); assert paths and all(p.startswith('/opt/prisma/') for p in paths), paths"
+    /app/.venv/bin/python -c "from prisma.client import BINARY_PATHS; paths = list(BINARY_PATHS.query_engine.values()); assert paths and all(p.startswith('/opt/prisma/') for p in paths), paths"
```

The three substitutions are atomic. Changing only the assertion is rejected because it exposes but does not repair the managed-interpreter venv. Changing only the sync selectors is rejected because a future broken or absent venv executable could again be masked by PATH fallback in the final assertion

### Portability Decision

APPROVE the portability assumption only under the existing exact builder/runtime package contract. Both stages install `python-3.13=3.13.15-r4` from the same digest-pinned Wolfi base, and `/usr/bin/python3.13` is therefore the intended stable base executable on both sides of the copied venv. The absolute selector is preferable to `--no-managed-python` or a global uv environment switch because it identifies the exact approved interpreter without broadening later uv behavior

This approval does not claim general cross-image venv portability. It is invalid if the builder or runtime Python package/version, base image, venv location, interpreter path, target architecture, or copy contract changes. Arm64 remains unauthorized until native arm64 build and runtime evidence exists. Any missing `/usr/bin/python3.13`, managed-Python download, venv link outside runtime-available system paths, builder/runtime package drift, or ABI mismatch must fail the candidate rather than trigger a fallback

Do not add or reorder runtime `PATH`, set `VIRTUAL_ENV`, change `ENTRYPOINT` or `CMD`, add `UV_PYTHON_DOWNLOADS`, add `--no-managed-python`, copy uv's managed interpreter store, or replace the absolute path with a name-based selector. The existing venv-first runtime PATH and `prod_entrypoint.sh` lookup are intentionally preserved

### Exact Developer Constraints

[Agent Message] From: tech_lead To: developer

Modify only the root `Dockerfile` with the exact three substitutions recorded above. Preserve every other byte in that file, including the Python `3.13.15-r4` builder/dev/runtime pins, Rust OCI stage and assertions, builder/runtime environment, Prisma environment, copy layout, `ENTRYPOINT`, and `CMD`. Do not edit locks, Cargo files, application source/tests, alternate Dockerfiles, scripts, configuration, credentials, images, deployment, or production

Before handback, prove the diff contains exactly two `python3.13` to `/usr/bin/python3.13` selector replacements and one final `python` to `/app/.venv/bin/python` assertion replacement. Run `git diff --check`. Record pre-change Dockerfile SHA-256 `30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c` and the new post-change SHA-256. Record a scoped diff showing no change to runtime `ENV`, `ENTRYPOINT`, `CMD`, Python APK pins, Rust lines, or any non-Dockerfile path

Produce `.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/SUMMARY.md` and secret-free logs. The summary must map `AC-1` through `AC-5`. Evidence must include the exact diff, diff check, pre/post fingerprints, preserved-file fingerprints, the replacement ordered manifest, and both replacement patch checksums. A bounded amd64 probe may be used to prove `/usr/bin/python3.13` exists in the exact Wolfi input and that uv creates a venv without downloading managed CPython; do not treat that probe as the complete candidate build or runtime smoke

Do not run or claim TASK-006's complete build/smoke unless PMA explicitly reopens and assigns it. Do not weaken or work around a failed selector, venv-link, fingerprint, provenance, or ABI check. No deployment, production restart/replacement, production credential/database access, or arm64 promotion is authorized

### Evidence And Re-Freeze Requirements

The replacement candidate remains based on Git commit `9af49e5b34e25cdc9ad40f9bb50a178f40320417` and must retain exactly the same ordered eight-path set used by TASK-006 Reopen 2. Only the root `Dockerfile` fingerprint may change. The seven preserved path fingerprints must remain:

```text
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
886d5b443d75e6477bd8f609543bdf0160f9105ce71c137f7f6426791f0d308f  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

Write the new Dockerfile fingerprint as the first line, recompute the ordered line-oriented eight-path manifest SHA-256, and independently review both before TASK-006 resumes. Recompute the combined tracked binary patch SHA-256 from the authorized base; the application-only tracked patch must remain `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`. The prior combined patch `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`, prior manifest `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`, and prior Dockerfile fingerprint are superseded for candidate authorization after implementation and must not be reused

Require unchanged supplementary fingerprints: parser `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`, `pyproject.toml` `3b8240e1f70307caf0c1641639577060eda2d7070b8962a008f91dc949b12117`, `uv.lock` `a7cc57875c67de85bbae0f82b834f31fc9d0c029073ef29e0883787a31a985e8`, `litellm-rust/Cargo.toml` `65cb1ec9ed32ebc0f450c0649a03159943a1f21625f61f1c993448b2ff60b83a`, and `litellm-rust/Cargo.lock` `ef6ae9d1e34b0bf82d93f06a3ef62694a1489a2a890b3cadecdbd74120e2273d`. Retain Wolfi OCI index `sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`, Rust OCI index `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`, and Rust amd64 platform manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`. Abort on any mismatch

After Developer handback, Tech Lead must independently inspect the exact diff and recompute the Dockerfile fingerprint, all seven preserved path fingerprints, ordered manifest checksum, combined tracked patch, unchanged application-only patch, parser/lock/Cargo fingerprints, and OCI provenance. Only that review may re-freeze the corrected candidate and authorize TASK-006 Reopen 3

TASK-006 Reopen 3 must build only `linux/amd64` with `--pull=false`. Build evidence must show APK system CPython `3.13.15-r4`, both uv commands selecting `/usr/bin/python3.13`/CPython 3.13.15, no managed CPython download, successful frozen syncs, Rust assertions and Maturin bridge build, Prisma generation, and the explicit venv assertion. Final-image evidence must directly invoke `/app/.venv/bin/python` and prove Python 3.13.15, venv prefix `/app/.venv`, system base prefix, target `cpython-313` SOABI, runtime-resolvable venv interpreter linkage, imports of Prisma, uvloop 0.21.0, LiteLLM, and `litellm.rust_bridge._native`, and Prisma query-engine paths under `/opt/prisma`

The final image config must preserve venv-first `PATH`, absent `VIRTUAL_ENV`, unchanged Prisma environment, and unchanged `ENTRYPOINT`/`CMD`. TASK-006 must then run the normal entrypoint in its isolated secret-free container and complete every previously authorized readiness, LazyMCP discovery/challenge, initialize/tool where safely available, reconnect, `/mcp`, MCP REST, upstream-preservation, production-invariant, and cleanup gate. A failed or blocked required gate cannot be converted to success

### Acceptance Criteria Coverage

- **AC-1: PASS.** TASK-011's exact three substitutions, raw Reopen 2 evidence, portability assumptions, alternatives, and fail-closed boundary were independently reviewed and approved
- **AC-2: PENDING DEVELOPER.** Authorization is limited to two absolute uv selectors and one explicit final assertion interpreter in the root Dockerfile
- **AC-3: PENDING DEVELOPER/TASK-006.** Exact build, final-image ABI/import/linkage, normal-entrypoint, PATH, and protocol gates are defined and must pass
- **AC-4: PENDING DEVELOPER.** Locks, Cargo files, source/tests, alternate Dockerfiles, production, and deployment are prohibited from changing and require fingerprint/diff evidence
- **AC-5: PENDING DEVELOPER/TECH LEAD.** New Dockerfile, manifest, and combined-patch fingerprints require Developer production and independent Tech Lead review before TASK-006 resumes

### Documentation Impact

No product or steady-state architecture documentation is required. This correction restores the already intended copied-venv/runtime contract and does not change the approved LazyMCP behavior, public interface, source-module structure, or CodeMap commands. Task and evidence closure remain mandatory

### Open Risks

The corrected candidate has not been implemented or built. Absolute selection should prevent uv's managed-interpreter fallback, but the actual venv link shape, system base prefix, copied native-extension ABI, Prisma engine loading, and normal entrypoint remain build/runtime gates. The live Wolfi APK transaction remains a broader reproducibility risk despite exact Python package constraints. Arm64 remains unauthorized. Repository-wide `staticeng_validate` is still affected by the known pre-existing missing-CodeMap inventory and is not evidence for or against these three substitutions

### Recommended Next Step

PMA should route the exact bounded handoff to Developer. Return the root Dockerfile, TASK-012 evidence packet, and replacement fingerprints to Tech Lead for independent post-implementation review. Keep TASK-006 closed until that review re-freezes the corrected candidate; keep deployment and production mutation unauthorized

## Developer: Post Implementation Expectations

### Summary

[Agent Message] From: developer To: product_manager

Implemented exactly the three approved root `Dockerfile` substitutions. Both uv selectors now use `/usr/bin/python3.13`, and the final Prisma assertion uses `/app/.venv/bin/python`. No full TASK-006 build/smoke, deployment, production action, commit, or push was performed

### Work Performed

Produced the exact task diff, static contract checks, `git diff --check` result, pre/post Dockerfile fingerprints, preserved fingerprints, replacement ordered eight-path manifest, and application/combined patch checksums under `.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/`

### Acceptance Criteria Coverage

- **AC-1: PASS.** Implemented under the recorded Tech Lead approval
- **AC-2: PASS.** Exactly three substitutions were applied to root `Dockerfile`
- **AC-3: PARTIAL, DEFERRED.** Static preservation checks pass; complete ABI/import/linkage/entrypoint/runtime checks remain TASK-006 gates
- **AC-4: PASS.** Preserved fingerprints match, and no prohibited implementation or operational scope was touched
- **AC-5: READY FOR TECH LEAD REVIEW.** Post-change Dockerfile SHA-256 is `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`, ordered manifest SHA-256 is `7b385506ab41f401bb1b6f925611fa3ba793884ea84db8bf3d6c9ff7bb534337`, and combined patch SHA-256 is `712f8bb20e3a3681694cd523c819d2c9fcfb6a2a99be015f12aee41a75fcf7da`

### Documentation Impact

No product, architecture, or CodeMap documentation change is required

### Open Risks

The corrected candidate has not been built. TASK-006's complete amd64 ABI, linkage, import, normal-entrypoint, and smoke gates remain pending. Arm64 remains unauthorized

### Recommended Next Step

Route the implementation and evidence packet to Tech Lead for independent review and candidate re-freeze. Do not reopen TASK-006 until that review passes

## Tech Lead Post-Implementation Review

### Summary

[Agent Message] From: tech_lead To: product_manager

Verdict: PASS. No blocking findings remain in TASK-012. The current root `Dockerfile` contains exactly the three authorized substitutions: both uv sync selectors use `/usr/bin/python3.13`, and only the final Prisma assertion explicitly invokes `/app/.venv/bin/python`. The implementation preserves the approved runtime environment, entrypoint contract, Python/Rust pins, locks, Cargo files, application candidate, alternate Dockerfiles, production, deployment, and arm64 boundary

### Work Performed

Independently reconstructed the pre-TASK-012 Dockerfile by reversing only the three approved substitutions. Its SHA-256 is `30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c`, exactly the frozen pre-change value. The current Dockerfile SHA-256 independently recomputes to `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`. Static inspection finds exactly two absolute uv selectors, no old name-based selectors, exactly one explicit venv Prisma assertion, and no other TASK-012 Dockerfile substitution. `git diff --check` passes

Independently recomputed all eight candidate path fingerprints and the ordered line-oriented manifest SHA-256 `7b385506ab41f401bb1b6f925611fa3ba793884ea84db8bf3d6c9ff7bb534337`. Independently recomputed the six-application-path tracked binary patch from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` as unchanged `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`, and the replacement Dockerfile-plus-six-path tracked binary patch as `712f8bb20e3a3681694cd523c819d2c9fcfb6a2a99be015f12aee41a75fcf7da`

Independently recomputed `pyproject.toml`, `uv.lock`, `litellm-rust/Cargo.toml`, and `litellm-rust/Cargo.lock`; every fingerprint matches the frozen evidence and all four have an empty working-tree diff. The seven application/parser path fingerprints are unchanged. Root Dockerfile inspection confirms the runtime remains venv-first, `VIRTUAL_ENV` remains absent, Prisma environment is unchanged, `ENTRYPOINT` and `CMD` are unchanged, builder/runtime Python remain exactly `3.13.15-r4`, and the approved Rust OCI stage/assertions are unchanged. TASK-012 introduced no alternate-Dockerfile, entrypoint-script, source, test, lock, Cargo, production, deployment, or arm64 drift

Independent results are recorded in `.staticeng/evidences/TASK-2026-08-31-012-pin-venv-system-python/logs/06-tech-lead-independent-review.log`

### Acceptance Criteria Coverage

- **AC-1: PASS.** Prior Tech Lead review approved the exact atomic correction and bounded portability assumption
- **AC-2: PASS.** Independent reconstruction proves exactly the two absolute uv selectors and one explicit venv assertion changed in the root Dockerfile
- **AC-3: PASS FOR TASK-012 SCOPE.** Static preservation and fail-closed interpreter selection pass; complete image ABI, imports, linkage, normal entrypoint, and runtime behavior remain mandatory TASK-006 Reopen 3 gates and are not pre-claimed
- **AC-4: PASS.** Locks, Cargo files, candidate source/parser, alternate Dockerfiles, runtime environment/entrypoints, production, deployment, and arm64 scope are preserved
- **AC-5: PASS.** Dockerfile, eight-path manifest, combined patch, application-only patch, parser, lock, Cargo, and OCI inputs are independently reviewed and re-frozen below

### Documentation Impact

No product, architecture, operator, or CodeMap documentation change is required. TASK-012 restores the intended copied-venv interpreter provenance without changing public behavior or module structure. Task and evidence closure are complete for technical review

### Open Risks

TASK-012 proves the bounded source correction and frozen inputs, not a successful candidate image. Venv symlink resolution, system base prefix, Python 3.13.15 ABI/SOABI, copied native extensions, Prisma engines, uvloop, Rust bridge, normal startup, and LazyMCP smoke remain TASK-006 Reopen 3 gates. Wolfi APK resolution remains live beyond exact Python constraints. Arm64 remains unauthorized. `staticeng_validate` remains blocked by the known pre-existing missing-CodeMap inventory and no unrelated repair is authorized

### TASK-006 Reopen 3 Frozen Authorization

[Agent Message] From: tech_lead To: qa_engineer

Authorize TASK-006 Reopen 3 candidate construction and isolated amd64 smoke from exact Git base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`. Use build/runtime OCI index `cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`, uv OCI index `ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a`, Rust OCI index `docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`, and require Rust amd64 platform manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`. The Rust arm64/v8 manifest `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d` remains provenance only and authorizes neither arm64 build nor promotion

Construct a clean detached worktree under `/tmp/opencode` containing exactly this ordered eight-path manifest and no other shared-worktree change:

```text
ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc  Dockerfile
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
886d5b443d75e6477bd8f609543bdf0160f9105ce71c137f7f6426791f0d308f  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

Require ordered line-oriented manifest SHA-256 `7b385506ab41f401bb1b6f925611fa3ba793884ea84db8bf3d6c9ff7bb534337`. Apply/reproduce only the Dockerfile plus six tracked application-path binary patch whose SHA-256 from the base is `712f8bb20e3a3681694cd523c819d2c9fcfb6a2a99be015f12aee41a75fcf7da`; copy the untracked parser separately and require its fingerprint above. Require unchanged six-application-path tracked patch SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`

Before build, require `pyproject.toml` SHA-256 `3b8240e1f70307caf0c1641639577060eda2d7070b8962a008f91dc949b12117`, `uv.lock` `a7cc57875c67de85bbae0f82b834f31fc9d0c029073ef29e0883787a31a985e8`, `litellm-rust/Cargo.toml` `65cb1ec9ed32ebc0f450c0649a03159943a1f21625f61f1c993448b2ff60b83a`, and `litellm-rust/Cargo.lock` `ef6ae9d1e34b0bf82d93f06a3ef62694a1489a2a890b3cadecdbd74120e2273d`. Abort on any base, path set, fingerprint, patch, manifest, OCI index/platform, package resolution, interpreter selection, Rust assertion, or provenance mismatch

Build only `linux/amd64` with `--pull=false` and record immutable candidate image identity. Build evidence must show APK system CPython `3.13.15-r4`; both uv commands must select `/usr/bin/python3.13`/CPython 3.13.15 and must not download managed CPython. Require both frozen syncs, Rust assertions, Maturin/Rust bridge build, Prisma generation, and explicit `/app/.venv/bin/python` final assertion to pass

In the final image, directly invoke `/app/.venv/bin/python` and prove Python `3.13.15`, `sys.executable == '/app/.venv/bin/python'`, `sys.prefix == '/app/.venv'`, system base prefix, target `cpython-313` x86_64 SOABI, and runtime-resolvable linkage to installed `/usr/bin/python3.13`. With a minimal safe PATH, require imports of `prisma`, `uvloop`, `litellm`, and `litellm.rust_bridge._native`; require uvloop `0.21.0`, nonempty Prisma query-engine paths under `/opt/prisma`, and available native Rust bridge

Inspect final image config and require unchanged venv-first PATH, absent `VIRTUAL_ENV`, unchanged Prisma environment, and unchanged `ENTRYPOINT`/`CMD`. Run the normal entrypoint, not an overridden Python command, in TASK-006's isolated secret-free container. Complete every original TASK-006 gate: readiness; all six LazyMCP discovery aliases and exact canonical resources; exact no-token and invalid-token challenges; safely available authorized initialize/tool behavior; repeated reconnects with zero discovery 404s; `/mcp`; MCP REST; upstream-preservation checks; production pre/post immutable identity and readiness; and complete candidate worktree/container/network cleanup. Mark credential-bound checks blocked rather than weakening them, but do not convert any failed required gate to success

This authorization permits detached candidate construction and isolated amd64 smoke only. It does not authorize deployment, production restart/replacement, production credentials or databases, data/configuration mutation, arm64 execution/promotion, or reuse of the superseded Reopen 2 Dockerfile, manifest, or combined-patch fingerprints

### Recommended Next Step

PMA should mark TASK-012 technically reviewed and reopen TASK-006 as Reopen 3 with the exact QA authorization above. Return immutable image identity and complete secret-free evidence for final technical review before any promotion decision

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-012 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
