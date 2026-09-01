---
id: TASK-2026-09-01-008-design-upstream-main-integration
complexity: complex
track: investigation
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-010-integrate-upstream-main
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design upstream main integration

## Objective

Map current dirty fork work, origin/upstream topology, merge conflicts, test surfaces, isolated-build strategy, and sequential Git/Fedora release gates before implementation.

## Acceptance Criteria

- [ ] AC-1: Classify every tracked/untracked dirty path by existing task/intent and identify a safe pre-merge commit sequence.
- [ ] AC-2: Compare merge versus replay and recommend the least destructive strategy consistent with preserving fork `main` history and incorporating all upstream commits.
- [ ] AC-3: Produce a read-only conflict/impact map against exact upstream `main`, including dependency/lock, Dockerfile, MCP/LazyMCP, Responses, UI, migrations, and StaticEng artifacts.
- [ ] AC-4: Define atomic implementation slices, exact tests, isolated Docker topology, qualification, registry, fork-main push, Fedora deployment, and rollback.
- [ ] AC-5: Identify operations requiring Tech Lead commit/push authorization and all stop gates.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Research only. Inspect current working tree, origin/main, remote upstream/main, prior task/evidence ownership, and perform read-only merge simulation. Do not fetch, merge, rebase, edit, stage, commit, push, build, or mutate hosts. Update this task with an implementation-ready signed architecture handoff.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

Read-only architecture research is complete. The fork is not ready for integration: `main` and `origin/main` are both `9af49e5b34e25cdc9ad40f9bb50a178f40320417`, but the worktree has 28 tracked modifications and 2,138 untracked paths. No files are staged. The local `upstream/main` ref is stale at `418c7c6012d7c39a9d4a28c72cabe1995595ad2b`; remote read-only inspection reports exact current upstream `main` as `10631eb834c7802aa61611e807474170b8a4d425` from 2026-08-30. Therefore the cached merge simulation is a lower bound only and implementation must begin with an authorized fetch plus a new exact-object simulation

The recommended strategy is a normal no-fast-forward merge of exact reviewed upstream `main` into cleaned fork `main`, not replay/rebase. The fork already contains a prior upstream merge (`5ef381ed29e92a759f2ada0f4bba32fd3f8579b2`), has 190 fork-side commits versus 2,376 upstream-side commits at remote merge base `bc6e7df05b018eefe6c7293790ca3f4de38709ac`, and must preserve published fork history. A replay would rewrite all fork-only commits and require a force update; a merge retains both histories and incorporates every upstream commit by ancestry

### Work Performed

#### Exact Topology And Read-Only Simulation

- Canonical checkout: `/home/staticduo/git/litellm`; branch `main`; `HEAD == origin/main == 9af49e5b34e25cdc9ad40f9bb50a178f40320417`; branch divergence from origin is `+0/-0`
- `origin` fetch/push URL is `git@github.com:jibanez-staticduo/litellm.git`; `upstream` fetch URL is `https://github.com/BerriAI/litellm`; upstream fetch refspec is restricted to `main`
- Read-only `ls-remote` proves `origin/main=9af49e5b34e25cdc9ad40f9bb50a178f40320417` and current remote `upstream/main=10631eb834c7802aa61611e807474170b8a4d425`. The latter object is not present locally because fetch was prohibited
- Cached local `upstream/main=418c7c6012d7c39a9d4a28c72cabe1995595ad2b` has merge base `bc6e7df05b018eefe6c7293790ca3f4de38709ac` with fork `HEAD`; cached divergence is 190 fork commits and 860 upstream commits. Remote GitHub comparison at current tips reports the same merge base, 190 fork-side and 2,376 upstream-side commits
- A read-only `git merge-tree` against the cached upstream ref finds 16 textual conflict files and 50 conflict hunks: `Makefile`; Responses bridge handler/test; MCP manager/server; budget reset; proxy pre-call/server/utils; Responses MCP handler; fallback handler/test; auth test; secret-redaction test; MCP dashboard connect; and generated UI schema. This is not authoritative for current upstream
- Read-only current-upstream tree comparison finds 4,666 upstream-changed blobs since the merge base, 1,001 fork-changed paths, and 89 overlapping paths. Current upstream additionally changed active dirty MCP/OAuth seams, including admission auth, discovery, DCR, session tokens, server, and proxy wiring. Exact conflict count must be recomputed after fetch

#### Dirty Work Ownership And Pre-Merge Commit Sequence

All 28 tracked modifications are unstaged and attributable from task/evidence records:

1. **DeepSeek hosted-vLLM contract:** seven tracked paths, 511 additions and 20 deletions, plus untracked `litellm/llms/hosted_vllm/reasoning_policy.py`. Owner is `TASK-2026-08-25-003-implement-deepseek-hosted-vllm-policy`; the task records 59 focused tests, Ruff, focused basedpyright, and no commit
2. **LazyMCP OAuth discovery/audience/toolset contract:** 13 tracked paths, 855 additions and 53 deletions, plus untracked `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py` and `tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py`. Owners are `TASK-2026-08-31-003-implement-lazymcp-oauth-discovery` through `TASK-2026-08-31-017-final-review-lazymcp-oauth`; source/candidate closure passed while promotion remained blocked
3. **Candidate build foundation:** root `Dockerfile`, 36 additions and 10 deletions. Owners are packaging tasks `TASK-2026-08-31-008`, `010`, `012`, and `014`; it pins the Wolfi base, Python 3.13, Rust 1.97.1, and venv interpreter. This is release-critical source, not disposable candidate residue
4. **StaticEng closure state:** seven tracked registry/evidence files, 139 additions and 28 deletions, plus untracked SCRs, architecture docs, 234 evidence files, 72 task files, and `.opencode/plans/*`. These are orchestrator/closure artifacts from the DeepSeek, LazyMCP, client-model, and current upstream-integration workflows
5. **Repository-wide CodeMaps:** 1,823 untracked `codemap.yml` files generated during pre-existing StaticEng repair/init work. Prior task records consistently classify the repository-wide missing-CodeMap inventory as unrelated global debt requiring module-boundary decisions. This bulk set must not be folded into feature or upstream integration commits without a separate Tech Lead disposition

The only untracked non-StaticEng/non-CodeMap source paths are the three task-owned files named above. No unknown product source was found

Safe pre-merge sequence for `TASK-2026-09-01-009`, under Tech Lead commit authority:

1. Snapshot status, diff, hashes, and secret scan; verify no concurrent owner is editing the worktree. Stop on drift
2. Commit DeepSeek source, tests, contract/SCR, nearest CodeMaps, and task evidence as one logical `feat` commit after rerunning its focused gates
3. Commit LazyMCP OAuth source, tests, architecture contract/SCR, nearest CodeMaps, and task evidence as one logical `feat` commit after rerunning its final focused/mapped/security gates
4. Commit candidate `Dockerfile` packaging foundation as one logical `build` commit after revalidating exact OCI/package identities and Dockerfile contract checks. Do not reuse the rejected candidate identity
5. Commit remaining reviewed StaticEng closure/registry artifacts in logical `docs` commits, preserving task ownership. Include current upstream-integration task/SCR records only when PMA considers them closure-ready
6. Quarantine or separately disposition the 1,823 bulk CodeMaps and `.opencode/plans`. Do not stage them by broad path or `git add -A`; never delete them merely to clean the tree
7. Require a final clean `git status --porcelain=v1 --untracked-files=all`, no staged residue, exact `HEAD==origin/main` unless authorized local commits are intentionally ahead, and an explicit owner acknowledgment for every preserved-outside-integration path

#### Current-Upstream Impact Map

The exact reviewed target is remote commit `10631eb834c7802aa61611e807474170b8a4d425`. It includes the RestrictedPython remediation verified in `TASK-2026-09-01-006`: declaration and lock at 8.5, above the advisory's fixed threshold. The following surfaces require explicit merge ownership and verification:

- **Dependencies and locks:** accept upstream `pyproject.toml`, `uv.lock`, root version 1.99.0, proxy-extras version, Cargo manifests/lock, UI `package.json`/`package-lock.json`, and quality budgets as the baseline. Reapply only documented fork constraints. Verify `RestrictedPython>=8.5,<9.0` and lock 8.5 after resolution; never retain fork 8.1
- **Docker/supply chain:** current upstream changed root `Dockerfile` after the cached ref. Three-way reconcile upstream base-security changes with fork Wolfi/Python/Rust/venv determinism. Re-resolve every external OCI digest and platform child, then rebuild all SBOM/scan/provenance evidence. The rejected prior image and its manifests are invalid for the merged source
- **MCP/LazyMCP/OAuth:** highest-risk boundary. Current upstream changed `user_api_key_auth_mcp.py`, `discoverable_endpoints.py`, `gateway_dcr_flow.py`, `session_token.py`, `server.py`, and `proxy_server.py`, including RS256 session-token and introspection work. Preserve exact LazyMCP public-resource identity, challenge, audience isolation, admission-before-toolset lookup, no inbound-token forwarding, prior LazyMCP catalog behavior, and upstream's new signing/introspection contracts
- **Responses/ChatGPT/model routing:** cached conflicts include Responses bridge/MCP handlers and fallback logic; current overlap includes ChatGPT authentication/Responses transforms, OpenAI Responses, HTTP handler, router, and fallback paths. Preserve fork native ChatGPT streaming, stream-failure serialization, usage normalization, multi-account/fallback behavior, and DeepSeek final-payload validation while adopting upstream interfaces
- **UI:** upstream has a large dashboard refactor and package/lock update. MCP UI files overlap, and generated `src/lib/http/schema.d.ts` conflicts. Preserve fork LazyMCP connection behavior but adopt upstream form/test architecture. Never hand-resolve generated schema; resolve backend routes first, run `npm run gen:api`, then verify generated-only delta
- **Migrations/schema:** upstream adds/removes proxy-extras migrations and changes both root and proxy-extras Prisma schemas. Treat migrations as append-only ordered history; do not squash, rename, or edit an already published migration to resolve names. Run schema generation/validation and migration tests against a disposable empty database and a sanitized copy/fixture representing the current Fedora schema. Database rollback is restore-from-backup or forward-fix, never down-migration assumption
- **StaticEng/CodeMaps:** upstream has no ownership of fork `.staticeng` history, so retain fork artifacts. Update only CodeMaps for actual added/moved merged source and commands. Keep global bulk-CodeMap debt separate. Run `staticeng_validate`; if it fails on the established unrelated inventory, run required repair dry-run and record exact baseline/delta without broadening the integration

#### Atomic Implementation Slices And Stop Gates

1. **Pre-merge closure (`TASK-009`, Tech Lead):** commit all intended dirty work in the sequence above. Stop if ownership is ambiguous, tests fail, secrets appear, current owners are active, bulk CodeMaps cannot be safely separated, or the worktree is not clean
2. **Freeze target and branch (Tech Lead):** authorized `git fetch upstream main`; verify fetched `upstream/main` equals reviewed `10631eb...`. If remote moved, stop and return to PMA for a new reviewed target. Create a task branch/worktree from clean fork `main`; never integrate in the dirty canonical worktree
3. **Integration skeleton (Developer):** run a no-fast-forward merge without auto-commit against the frozen object, record all conflicts and auto-merges, and resolve infrastructure/dependencies first. Stop on unexplained path drift, unexpected submodule/LFS content, secret files, migration-name collision, or deletion of fork source without an explicit upstream-equivalence proof
4. **Behavior reconciliation (Developer):** resolve MCP/LazyMCP/OAuth, Responses/ChatGPT/routing, UI, and generated artifacts by contract, not by choosing ours/theirs wholesale. Use upstream interfaces and the smallest fork-specific delta. Record each conflict's owner, decision, and test
5. **Source qualification (Developer then independent QA/Tech Lead):** run exact gates below. No required skip, xfail, flaky retry acceptance, lint/type budget increase, lock drift, generated drift, or unresolved conflict marker is allowed
6. **Integration commit (Tech Lead):** review status/diff/log, upstream ancestry, conflict ledger, tests, docs, CodeMaps, and evidence. Commit only after approval. No push in `TASK-010`
7. **Isolated candidate (`TASK-011`, QA):** build from a clean detached worktree under `/tmp/opencode`, with a task-owned network, PostgreSQL, Redis if required, volumes, ports, credentials, and config. No Fedora/NAS mounts, networks, DBs, credentials, or selectors. Retain builder/final immutable identities and full security packet
8. **Release (`TASK-012`, Tech Lead):** after independent approval, non-force push reviewed commits to fork `main`; publish the exact qualified digest; deploy Fedora only; observe and roll back on any gate. NAS remains untouched

Mandatory stop gates: target SHA mismatch; non-clean pre-merge tree; unowned dirty path; merge-base change; unexpected force-push requirement; unresolved conflict/marker; dependency or lock inconsistency; RestrictedPython below 8.5; schema/migration validation failure; generated API drift; source/lint/type/test failure or skip; candidate/build identity mismatch; unsigned/unattested candidate; missing builder/final SBOM; fixable High/Critical finding; absent candidate-bound real tool invocation; Fedora baseline/rollback gap; any NAS mutation; any post-approval source/image drift

#### Exact Verification Plan

Run commands from the merged clean task worktree and retain full logs. Resolve command drift against the merged `Makefile`/CodeMaps before execution

- **Git/integration:** `git diff --check`; `git diff --name-only --diff-filter=U` must be empty; conflict-marker scan; `git merge-base --is-ancestor 10631eb834c7802aa61611e807474170b8a4d425 HEAD`; preserve pre-integration fork tip as ancestor; compare fetched target tree and commit count; verify no secret-bearing or unexpected binary files
- **Dependency/compile:** `uv lock --check`; verify RestrictedPython declaration/lock 8.5; `uv sync --frozen` in an isolated environment; `python -m compileall` or repository mapped compile gate for touched Python; `cargo check --locked` and mapped Rust tests when Cargo changed; Prisma format/validate/generate and migration test commands from merged repository
- **Quality:** targeted Ruff format/check for every touched Python path; focused basedpyright plus repository `make check` and `make lint` with long timeout; run all ratchet/budget gates and reject any raised ceiling. UI: `npm ci`, `npm run format:check`, `npm run lint`, `npm run test:types`, `npm run test -- --run`, `npm run knip:ci`, `npm run build`, and `npm run gen:api` verification
- **DeepSeek/model policy:** both hosted-vLLM mapped files, including all 59 prior target/unrelated-model cases; sync/async, stream/non-stream, Chat/Responses, extra-body conflict and zero-forwarding matrices. Add/retain model routing, fallback, ChatGPT auth/profile/native-stream, Responses usage/serialization, and router regression suites implicated by overlaps/conflicts
- **MCP/LazyMCP/OAuth:** rerun the final focused and full mapped suites from TASK-003, not only conflict files. At minimum include public-resource parser, discovery, gateway DCR, session token/signing/introspection, admission auth, MCP server/manager, dynamic routes, component allowlists, toolsets, permissions, upstream credential modes, Responses MCP handlers, and dashboard MCP tests. Require upstream RS256/introspection tests plus fork exact-audience/challenge tests in the same run
- **Proxy/security/preservation:** cached conflict tests for budget reset, pre-call utilities, proxy utils/server, auth, secret redaction, fallback events, spend/logging, startup/import, and component ownership. Verify no access-token, authorization-code, refresh-token, credential, or sensitive query leakage
- **Migrations:** empty-DB full migration, upgrade from sanitized current Fedora schema fixture, idempotent restart, schema drift check, expected table/index/constraint inventory, and application readiness after migration. Record backup/restore rehearsal before any release
- **StaticEng/docs:** nearest CodeMaps list all retained/new source; architecture contracts reflect final behavior; `staticeng_validate`, required repair dry-run on known baseline failure, and a no-new-finding delta report

#### Isolated Candidate, Qualification, Registry, Release, And Rollback

- Build only from the reviewed integration commit in a clean detached `/tmp/opencode` worktree. Use a uniquely named Docker network, PostgreSQL container/volume, optional Redis, LiteLLM container, and a task-local deterministic MCP test server. Bind only high loopback ports. Mount no host deployment directories and use synthetic task credentials
- Exercise readiness/liveness, migration startup and restart, model catalog/inventory, mocked deterministic provider paths for exhaustive translation tests, and authorized lower-risk real provider/model calls where explicitly approved. Run Chat Completions and Responses streaming/non-streaming, fallback/account selection, MCP REST, `/mcp`, all LazyMCP resource forms, discovery/challenges/DCR/code/refresh/audience replay, initialize/list/call, toolset/group/server permissions, reconnect, upstream credential isolation, and candidate-bound real registered tool success
- Retain immutable builder and final image IDs, OCI manifest/config/layer digests, source commit, Dockerfile and lock fingerprints, exact base/toolchain child digests, build logs, SPDX/CycloneDX SBOMs for builder and final images, same-database scans, signatures, attestations, provenance, and secret scan. Reject any fixable High/Critical vulnerability. The prior unsigned RestrictedPython-8.1 candidate is never promoted or retagged
- Publish first under a unique candidate tag, verify registry pull resolves byte-for-byte to the qualified manifest/config, then sign/attest that exact digest. Do not move a stable tag before Fedora observation and final authorization
- Before Fedora deployment capture current image selector/digest/config, Compose rendering, service/container identity, health, model projection, MCP registrations, route checks, relevant sanitized logs, DB migration level, backup/restore artifact, and rollback commands. Update only the Fedora LiteLLM image selector to the exact digest and recreate only the LiteLLM service
- Observe readiness, inventory, Chat/Responses, fallbacks, MCP/LazyMCP/OAuth/real tool, reconnects, migrations, and clean logs for the task-defined window. Stop and roll back on any regression, 401/403/404/5xx drift, missing model/server/tool, DB error, repeated reconnect failure, auth/audience leak, or container churn outside LiteLLM
- Rollback by restoring the recorded prior Fedora immutable digest/config selector and recreating only LiteLLM, then rerun the complete baseline. If an irreversible migration or failed restore rehearsal exists, deployment is prohibited. NAS image, selector, service, data, and routing remain unchanged throughout

#### Authorization Boundaries

- **Tech Lead required:** all staging and commits in `TASK-009`; authorized upstream fetch and integration branch/worktree creation; merge execution; conflict-resolution acceptance; integration commit; non-force push to fork `main`; candidate publication/signing/attestation; registry tag movement; Fedora selector/service mutation; rollback; and final workflow closure
- **Developer allowed only after activation:** edit/resolve/test in the isolated integration worktree and produce evidence. No commit, push, image publication, registry mutation, deployment, or host mutation
- **QA allowed only after source approval:** isolated build/test/security qualification and evidence. No fork-main push, stable promotion, Fedora/NAS mutation, or production credentials/mounts
- **Never authorized by this handoff:** force-push, rebase of published fork `main`, push to `upstream`, NAS deployment/mutation, reuse of rejected candidate identity/evidence, broad deletion of dirty work, or automatic bulk CodeMap inclusion

### Acceptance Criteria Coverage

- [x] **AC-1:** Every dirty path is classified into DeepSeek, LazyMCP OAuth, candidate packaging, StaticEng closure, global CodeMap debt, or `.opencode` plans. The three untracked product/test files are explicitly attributed. A safe logical commit sequence and final-clean gate are defined
- [x] **AC-2:** Merge versus replay is compared. No-fast-forward merge is recommended because it preserves published fork history, incorporates upstream by ancestry, avoids force-push, and matches the existing merge-based topology
- [x] **AC-3:** Cached read-only merge simulation identified 16 files/50 hunks; current exact remote SHA and 89 current overlap paths are mapped. Dependencies/locks, Dockerfile, MCP/LazyMCP, Responses, UI, migrations, and StaticEng impacts are explicitly covered
- [x] **AC-4:** Atomic pre-merge, integration, source QA, isolated candidate, security, registry, fork-main, Fedora-only release, observation, and rollback slices are defined with exact verification surfaces and topology
- [x] **AC-5:** Tech Lead-only operations and mandatory stop gates are explicit. Developer/QA boundaries and permanently prohibited operations are recorded

### Documentation Impact

This task file is the implementation-ready architecture decision and integration runbook. No product documentation changes are required because upstream integration does not itself add a fork product capability. During implementation, update steady-state architecture contracts only where final merged interfaces differ, and update nearest CodeMaps for actual source/layout/command changes. Run `staticeng_validate` after CodeMap or architecture changes and separate established global debt from new findings

### Open Risks

- The current upstream object is remote-only because fetch was prohibited. Conflict count and exact current-upstream diff remain provisional until authorized fetch freezes `10631eb...`; upstream may move again
- The shared worktree is extremely dirty. Broad staging, cleanup, or merge in place risks mixing accepted work, generated CodeMaps, and current orchestration state
- Current upstream adds MCP session-token signing/introspection changes on the same seams as fork LazyMCP audience binding. This is the highest security regression risk
- Upstream UI, generated API schema, dependencies, Rust, and migrations changed substantially. A textual merge can pass while generated, schema, or runtime contracts are inconsistent
- The release helper `/home/staticduo/git/release-litellm.sh` is unsafe for this workflow as written: it fetches/merges, pushes mutable stable tags, and deploys NAS before Fedora. Do not invoke it for TASK-012; use explicit Fedora-only, exact-digest, gated commands or a separately reviewed release correction
- Repository-wide StaticEng validation debt and 1,823 untracked CodeMaps remain unresolved. They must not mask new task-local CodeMap defects or be silently committed with the integration

### Recommended Next Step

PMA should accept this design, then activate `TASK-2026-09-01-009-finalize-premerge-fork-work` for Tech Lead-controlled logical commits and clean-tree closure. Only after that gate may PMA activate the integration task with an authorized fetch, exact SHA revalidation, and a fresh read-only merge simulation

## Signed Architecture Handoff

[Agent Message] From: technical_architect To: product_manager

IMPLEMENTATION-READY WITH PRECONDITIONS. Use a no-fast-forward merge, not replay, after Tech Lead commits the owned dirty work and obtains a clean worktree. Freeze remote upstream `main` at `10631eb834c7802aa61611e807474170b8a4d425`; stop if fetch resolves another SHA and return for re-review. Recompute conflicts against that exact object, preserve fork contracts through upstream interfaces, require complete source and isolated-candidate qualification, then non-force push fork `main` and deploy the exact approved digest to Fedora only. Do not invoke the current release helper because it can merge and mutate NAS. All push, publication, deployment, rollback, and commit operations require Tech Lead authorization
