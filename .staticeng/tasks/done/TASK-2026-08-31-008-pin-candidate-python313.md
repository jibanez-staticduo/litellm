---
id: TASK-2026-08-31-008-pin-candidate-python313
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: product_manager
handoff_from: tech_lead
reopened_count: 1
---

# Task: Pin candidate image to Python 3.13

## Objective

Apply the smallest deterministic packaging correction required to build the reviewed LazyMCP candidate: pin the root Dockerfile to the established Python 3.13.15 runtime while preserving `uvloop==0.21.0`, application source, locks, and production.

## Acceptance Criteria

- [x] AC-1: Tech Lead approves or rejects the exact five-line Dockerfile-only correction proposed by TASK-007.
- [x] AC-2: `Dockerfile` pins build/dev/runtime packages to `python-3.13=3.13.15-r4` and uv invocations to `python3.13`, with no other packaging change.
- [x] AC-3: `pyproject.toml`, `uv.lock`, application runtime source, tests, and production remain unchanged by this subtask.
- [x] AC-4: Focused Dockerfile review, diff check, and package-resolution/build evidence pass.
- [x] AC-5: Candidate manifest is re-frozen with Dockerfile fingerprint and handed back to TASK-006 for complete smoke.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/` with `SUMMARY.md`, exact diff/fingerprints, build logs, and signed Tech Lead authorization. No secrets.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review the TASK-007 architecture recommendation and current root Dockerfile. Approve or reject the exact five-line Python 3.13 pin. Do not edit files. If approved, update this task with signed authorization and exact package/version constraints for Developer. Production and deployment remain out of scope.

## Implementation Handoff

[Agent Message] From: product_manager To: developer

Implement only the Tech Lead-approved five substitutions recorded in this task's Reopen 1 review. Do not alter locks, application source/tests, other Dockerfiles, configuration, deployment, or production. Produce the TASK-008 Evidence Packet, run Dockerfile diff/static checks, verify unchanged `pyproject.toml` and `uv.lock`, then hand back for a newly frozen eight-path candidate manifest. Do not deploy or replace the production container.

## Tech Lead Review

[Agent Message] From: tech_lead To: product_manager

Verdict: REJECT. TASK-007 remains active and contains no findings, option comparison, exact five-line proposal, compatibility analysis, rollback, or signed architecture handoff. No TASK-007 evidence exists. The requested prerequisite therefore cannot be reviewed or attributed to TASK-007, and implementation is not authorized

The five inferred substitutions are technically scoped to the current Dockerfile locations: replace builder `python3` with `python-3.13=3.13.15-r4`, builder `python3-dev` with `python-3.13-dev=3.13.15-r4`, both `uv sync` selectors from `python3` to `python3.13`, and runtime `python3` with `python-3.13=3.13.15-r4`. This inference is not a substitute for TASK-007's required signed recommendation and package-availability evidence

Before renewed authorization, TASK-007 must record why the digest-pinned Wolfi base resolves Python 3.14.4, compare all four required alternatives, verify the exact package names and `3.13.15-r4` availability for the authorized build platforms, address builder/runtime ABI compatibility, and provide a signed recommendation with rollback

If a renewed review approves the pin, Developer evidence must include an exact five-line `Dockerfile` diff; pre/post Dockerfile SHA-256 fingerprints; proof that build and runtime package resolution selects Python 3.13.15-r4 on every authorized platform; proof both `uv sync` commands use Python 3.13; a successful immutable image build and runtime Python-version check; and a scoped diff proving `pyproject.toml`, `uv.lock`, application source, tests, deployment, and production are unchanged. Store secret-free artifacts under `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/`

## Reopen History

### Reopen 1: Governed TASK-007 Evidence Review

[Agent Message] From: product_manager To: tech_lead

Reopen TASK-008 review now that TASK-007 contains governed signed evidence. Review exact five-line proposal, amd64/arm64 package availability and ABI constraints, rollback, and manifest implications. Do not edit Dockerfile. Update TASK-008 review history and return findings first, approve/reject, and exact Developer handoff if approved.

### Tech Lead Findings And Authorization

[Agent Message] From: tech_lead To: product_manager

Verdict: APPROVE. The exact five substitutions in TASK-007 are the smallest deterministic correction and are authorized for Developer implementation in the root `Dockerfile` only

TASK-007 establishes exact `python-3.13=3.13.15-r4` and `python-3.13-dev=3.13.15-r4` availability in the current signed Wolfi indexes for both x86_64 and aarch64. Its native amd64 install probe confirms CPython 3.13.15, `cpython-313`, the x86_64 SOABI, `/usr/bin/python3.13`, and matching development headers. Arm64 package and dependency availability is established by its architecture-specific index, but arm64 execution is not established; any arm64 candidate or release remains fail-closed until built and runtime-validated on an arm64-capable builder

Builder/runtime ABI constraints are sound: both stages use the same digest-pinned Wolfi OCI index and exact Python runtime revision, `python-3.13-dev=3.13.15-r4` depends on that exact runtime revision, both frozen syncs select `python3.13`, and the copied virtual environment must remain `cpython-313`. Final-image evidence must also prove the runtime `python` command used by the existing Dockerfile resolves to Python 3.13.15, imports the copied extension set and `uvloop==0.21.0`, and reports the expected architecture-specific SOABI

TASK-007 understates the existing application manifest as six paths. TASK-006 records seven application paths; adding `Dockerfile` creates an eight-path candidate manifest. Developer must re-freeze all eight exact paths and fingerprints. The failed seven-path TASK-006 manifest and failed build are superseded as candidate inputs and cannot serve as runtime evidence

Rollback is adequate: before deployment, discard the candidate and revert only these five substitutions; after separately authorized promotion, redeploy the recorded prior immutable digest and verify health/baselines. Production and deployment remain outside TASK-008

### Exact Developer Handoff

[Agent Message] From: tech_lead To: developer

Implement exactly these five substitutions in the root `Dockerfile`: builder `python3` to `python-3.13=3.13.15-r4`; builder `python3-dev` to `python-3.13-dev=3.13.15-r4`; both `uv sync` selectors from `--python python3` to `--python python3.13`; and runtime `python3` to `python-3.13=3.13.15-r4`. Make no other packaging, source, test, lock, configuration, deployment, or production change

Fail closed if either exact package revision no longer resolves for an authorized platform. Capture the exact five-line diff, `git diff --check`, pre/post Dockerfile SHA-256, package-resolution logs, both frozen sync interpreter selections, and scoped unchanged proofs for `pyproject.toml`, `uv.lock`, the seven application paths, tests, configuration, deployment, and production. Build the amd64 candidate and validate final-image Python 3.13.15, `cpython-313`, architecture-specific SOABI, `python` and `python3.13` interpreter identity, `uvloop==0.21.0`, and representative copied-extension imports. If arm64 is included in the candidate authorization, perform the same build and runtime checks on an arm64-capable builder; index metadata alone is not runtime approval

Re-freeze an eight-path manifest containing the seven TASK-006 application paths plus `Dockerfile`, with exact fingerprints and immutable image identity. Store secret-free `SUMMARY.md` and logs under `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/`. Do not reuse the failed TASK-006 manifest as candidate evidence. Return the passing immutable candidate to PMA for reopened TASK-006 complete smoke; TASK-008 approval does not authorize deployment

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

Implemented exactly the five Reopen 1 substitutions in the root `Dockerfile`. The post-change Dockerfile SHA-256 is `2b64da5e532e2a6d7d10c5375784514c3982596e604c99feb352ea086706351c`. Exact package resolution passes for x86_64 and aarch64, while the native amd64 install probe reports Python 3.13.15, `cpython-313`, and `cpython-313-x86_64-linux-gnu`

PMA explicitly reserved the full candidate build and complete smoke for TASK-006, so no candidate image identity is claimed by this task. The eight-path input manifest is frozen in `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/logs/02-fingerprints-manifest.log`

## Acceptance Criteria Evidence

- **AC-1: PASS.** Reopen 1 signed authorization governed the implementation
- **AC-2: PASS.** Exact five-line root Dockerfile diff and static occurrence checks pass
- **AC-3: PASS.** Locks, seven application paths, tests, configuration, deployment, and production were not changed by TASK-008
- **AC-4: PASS FOR AUTHORIZED TASK-008 GATE.** Diff checks, exact package resolution, native amd64 ABI, and uvloop wheel checks pass; full candidate build is assigned to TASK-006
- **AC-5: PASS FOR INPUT FREEZE.** Eight exact input fingerprints are recorded for TASK-006; immutable image identity is pending its authorized build

Product documentation is not required because application behavior and architecture are unchanged. `staticeng_validate` remains blocked by pre-existing repository-wide missing CodeMaps unrelated to this Dockerfile-only task; focused validation passes

## Signed Completion Handoff

[Agent Message] From: developer To: product_manager

TASK-008 implementation is complete. Exactly five root `Dockerfile` substitutions pin Python 3.13.15-r4 and both uv selectors to `python3.13`; no other runtime/package file, lock, source, test, configuration, deployment, or production artifact was changed. The secret-free evidence packet records the exact diff, pre/post fingerprints, unchanged proofs, both-platform package resolution, native amd64 ABI result, uvloop 0.21.0 wheel compatibility, production invariants, and newly frozen eight-path candidate inputs. No full candidate build, deployment, commit, or push was performed. Reopen TASK-006 to build the candidate, record immutable image identity, validate final-image ABI/imports on each authorized platform, and execute complete smoke

## Tech Lead Post-Implementation Review

[Agent Message] From: tech_lead To: product_manager

Verdict: PASS. The implementation is exactly the authorized five substitutions in the root `Dockerfile`: two builder package replacements, two uv interpreter replacements, and one runtime package replacement. `git diff --check` passes, the current Dockerfile SHA-256 equals the frozen value, and no other Dockerfile line changed

`pyproject.toml`, `uv.lock`, and all seven application paths match the evidence packet fingerprints. The six tracked application-path binary patch remains SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`; the new parser remains SHA-256 `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`

Package and ABI evidence passes for TASK-008: exact Python runtime/development revisions resolve in signed x86_64 and aarch64 indexes, the native amd64 probe reports Python 3.13.15 and `cpython-313`, and the unchanged lock contains CPython 3.13 Linux uvloop 0.21.0 wheels for both architectures. Arm64 runtime execution and all final-image ABI/import assertions remain mandatory TASK-006 gates and are not inferred from index metadata

The newly frozen manifest contains exactly eight candidate paths. Its line-oriented SHA-256 manifest checksum is `5ffff56cabaa5cf064166b17bac3c67ed4f95f8b99a26fbacdee6fc1d7e6c5ef`. Product documentation is not required because this changes packaging determinism without changing application behavior or architecture

### TASK-006 Reopen 1 Authorization

[Agent Message] From: tech_lead To: qa_engineer

Authorize TASK-006 Reopen 1 from exact Git base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` using build and runtime OCI index `cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`. Construct the detached candidate from exactly these eight paths and fingerprints, with no other shared-worktree change:

```text
2b64da5e532e2a6d7d10c5375784514c3982596e604c99feb352ea086706351c  Dockerfile
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
886d5b443d75e6477bd8f609543bdf0160f9105ce71c137f7f6426791f0d308f  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

For deterministic reconstruction, the binary diff from that base for `Dockerfile` plus the six tracked application paths has SHA-256 `8fa57ee3dc13968fd66cff04d4309e707f6af940196af8cb05b6f9acfb7ef6c7`; copy the untracked parser separately and verify its fingerprint above. Abort on any base, path set, fingerprint, patch checksum, package-resolution, or OCI-index mismatch

Build amd64 with `--pull=false`, record immutable image identity, and validate final-image Python 3.13.15, `cpython-313`, architecture-specific SOABI, `python`/`python3.13` identity, uvloop 0.21.0, and representative copied extension imports before the complete TASK-006 smoke. Arm64 remains unauthorized for promotion unless an arm64-capable builder performs equivalent build and runtime validation. Preserve production invariants and cleanup requirements from TASK-006; this authorization permits candidate construction and isolated smoke only, not deployment

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-008 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
