# TASK-2026-09-01-013 Review Evidence

## Verdict

**REJECT / REOPEN TASK-010**

The open merge has the intended fork and upstream parents and no unresolved index entries, but it cannot be committed. Conflict preservation is materially false, required source gates are red or absent, a fixable npm High remains, and the proposed index omits required CodeMaps

## Findings

### 1. Blocker: conflict resolutions drop fork behavior and tests

Git records 45 conflicted paths in `.git/MERGE_MSG`. The proposed index contains 24 custom resolutions and 21 files byte-identical to upstream. The latter group includes source and tests where the fork parent had task-owned additions

The most direct behavioral loss is ChatGPT account isolation. The fork parent defines `allow_chatgpt_cross_profile_fallback`, `_chatgpt_auth_profiles`, `_is_cross_profile_fallback`, `validate_chatgpt_model_group_profiles`, immutable logical fallback identity, and ten focused regression tests. None is present in the proposed tree. This contradicts `CONFLICT_LEDGER.md` and `PRESERVATION_MANIFEST.md`, which say cross-profile prohibition and logical identity were combined with upstream behavior

The same upstream-identical pattern drops fork regression suites for LazyMCP admission/DCR/routes/catalog/toolsets, DeepSeek reasoning policy, native ChatGPT Responses streaming, empty-output recovery, cached-user auth dictionaries, spend-log NUL handling, bounded spend reads, and uvicorn redaction. Some implementation behavior may have moved or gained an upstream equivalent, but the ledger does not prove that equivalence and the mutation-sensitive tests are gone

Exact pre-commit fix: reopen each upstream-identical conflict, reconcile the fork delta through current upstream interfaces, restore mapped fork regressions at their final paths, and add per-path ledger evidence. An upstream-identical resolution is acceptable only when the Developer identifies the exact upstream equivalent and a retained test proves the same observable behavior

### 2. Blocker: `make check` is stale and still fails on real fork deltas

The recorded run used `LINT_BASE_REF=HEAD^`, which is not the integrated upstream baseline. It attributes the imported upstream snapshot to TASK-010 even though the committed budgets came from the exact upstream target

Failure classification:

| Logged failure | Classification | Disposition |
| --- | --- | --- |
| Ruff PT012 and PT011 in two tests | Integration regression, corrected after the log | Fresh targeted Ruff passes; rerun full `make check` after all fixes |
| Nine E2E basedpyright errors in `tests/e2e/proxy_client.py` | Integration regression, corrected after the log | Fresh focused basedpyright passes; rerun full gate |
| Strict `EXE002 +70` | Unrelated checkout-permission artifact plus invalid baseline | Files are `0777` on disk while the index has normal `100644` modes except the same three SAP Python files in both parents; normalize working-tree modes from the index or use a mode-correct isolated checkout, never raise the budget |
| Strict-rule deltas against `HEAD^` | Legitimate upstream baseline movement misattributed to this merge | Run against exact upstream `10631eb834c7802aa61611e807474170b8a4d425` |
| TQ002 `+25`, TQ008 `+481` against `HEAD^` | Mostly legitimate upstream baseline movement, with remaining fork-side debt | Exact-upstream rerun leaves TQ002 `+1` and TQ008 `+54`; fix tests or add individually justified suppressions, never raise the budget |
| basedpyright `reportArgumentType +285`, `reportCallIssue +5`, `reportUnnecessaryCast +5` against `HEAD^` | Mostly legitimate upstream baseline movement, with remaining fork-side debt | Exact-upstream rerun leaves `reportArgumentType +6`, `reportCallIssue +4`, `reportGeneralTypeIssues +3`, `reportPrivateUsage +8`, and `reportUnusedClass +2`; fix diagnostics without increasing ceilings |
| Type-discipline gate | Pass | No action beyond rerun |
| Dashboard format/lint/budgets/API generation | Pass with warnings | Rerun after lock and source changes |

Required gate commands before rereview:

```bash
LINT_BASE_REF=10631eb834c7802aa61611e807474170b8a4d425 make check
uv run --no-sync python scripts/ruff_strict_gate.py --base 10631eb834c7802aa61611e807474170b8a4d425
uv run --no-sync python scripts/test_quality_gate.py --base 10631eb834c7802aa61611e807474170b8a4d425
uv run --no-sync python scripts/type_check_gate.py --base 10631eb834c7802aa61611e807474170b8a4d425
```

The Developer must also make the local fallback choose the actual integration parent rather than silently using `HEAD^`, and cover in-progress and completed merge-parent selection with tests

### 3. Blocker: Rust source gate is absent

The merge changes 35 non-CodeMap Rust manifests, lock, source, benches, and tests. `cargo` is absent on this host, so the three attempted commands never executed. Rust validation is a source gate and cannot move to TASK-011

Use the repository's pinned, non-container CircleCI path under a task-local directory. On this verified `x86_64` host:

```bash
export RUSTUP_HOME=/tmp/opencode/TASK-2026-09-01-010-rust/rustup
export CARGO_HOME=/tmp/opencode/TASK-2026-09-01-010-rust/cargo
mkdir -p /tmp/opencode/TASK-2026-09-01-010-rust
curl -sSLf -o /tmp/opencode/TASK-2026-09-01-010-rust/rustup-init https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c /tmp/opencode/TASK-2026-09-01-010-rust/rustup-init | sha256sum -c -
chmod +x /tmp/opencode/TASK-2026-09-01-010-rust/rustup-init
/tmp/opencode/TASK-2026-09-01-010-rust/rustup-init -y --no-modify-path --profile minimal --default-toolchain 1.97.1
"$CARGO_HOME/bin/rustup" component add --toolchain 1.97.1 rustfmt clippy
```

Then run from `litellm-rust`:

```bash
"$CARGO_HOME/bin/cargo" +1.97.1 fmt --check
"$CARGO_HOME/bin/cargo" +1.97.1 clippy --workspace --all-targets --locked -- -D warnings
"$CARGO_HOME/bin/cargo" +1.97.1 clippy -p litellm-core --all-targets --features bedrock-auth --locked -- -D warnings
"$CARGO_HOME/bin/cargo" +1.97.1 test --workspace --locked
"$CARGO_HOME/bin/cargo" +1.97.1 test -p litellm-core --features bedrock-auth --locked
```

Retain versions, checksums, command logs, and exit codes. If non-container installation is not authorized, stop and obtain authorization for an isolated exact-toolchain runner; do not weaken or waive any command

### 4. Blocker: fixable npm High remains in the source lock

`npm audit --json` reports one High package with two advisories: transitive dev dependency `browserslist 4.28.2`, affected through `<=4.28.6`, with a fix available. The path is `eslint-config-next -> eslint-plugin-react-hooks -> @babel/core -> @babel/helper-compilation-targets -> browserslist`. `npm audit --omit=dev` reports zero vulnerabilities, so this is not a production runtime dependency

The fix remains blocking before source commit because the approved policy permits no fixable High and the candidate must derive from frozen reviewed locks. `npm audit fix --dry-run` selects `browserslist 4.28.8` and updates six transitive lock entries without a direct dependency change

Exact fix: run `npm audit fix --package-lock-only`, inspect the six lock-only updates, then run `npm ci`, all UI gates including the full unit suite, `npm audit --audit-level=high`, and `npm audit --omit=dev --audit-level=high`. TASK-011 must still scan exact builder/final images and independently disposition all findings; it cannot repair this source lock after approval

### 5. Blocker: the proposed commit omits required CodeMaps and review closure

Forty-two CodeMaps are untracked, including maps for ten new proxy-extras migrations, five new Rust directories, new Python/test modules, and new UI directories. `staticeng_validate` passes only because it reads those untracked files. The staged snapshot would not reproduce that pass

Exact fix: review all 42 maps against immediate local contents, stage the valid maps with TASK-010, rerun `staticeng_validate`, and prove the staged snapshot contains every file used by validation. Also include finalized TASK-010 evidence, this review disposition, and required task/registry closure before the eventual Tech Lead commit

### 6. Blocker: required test surfaces are missing

The packet has 1,499 focused Python passes and eight focused dashboard component tests, but no complete dashboard unit run. Ten new proxy-extras migrations and broad schema changes received Prisma syntax validation only, not empty-database migration, upgrade, restart, or drift checks. Rust did not run. These source gates are required before TASK-011 and cannot be deferred to candidate runtime qualification

Exact fix: after preservation and lock corrections, run the full mapped Python suites, full dashboard unit suite, source migration matrix defined by TASK-008, pinned Rust matrix, and the complete source gate. Retain exact command lines, test counts, skips/xfails, warnings, and exit status

### 7. Worktree disposition

The three unrelated unstaged StaticEng normalizations are:

- `.staticeng/evidences/TASK-2026-09-01-009-finalize-premerge-fork-work/SUMMARY.md`
- `.staticeng/tasks/todo/TASK-2026-09-01-002-design-dual-host-release.md`
- `.staticeng/tasks/todo/TASK-2026-09-01-008-design-upstream-main-integration.md`

Their common timestamp and exact path/link rewrites match the deterministic Markdown normalization that TASK-009's repair dry run explicitly classified as unrelated and not applied. Restore these three files to `HEAD` after confirming no owner claims them, or route them through a separate docs task. Do not stage them with TASK-010

`.staticeng/tasks/current.md`, this task, and this evidence are authorized TASK-013 review state, not part of those three normalizations. They still require deliberate final closure handling before any commit

## Acceptance Criteria Coverage

- **AC-1: PASS FOR REVIEW, MERGE FAIL:** all recorded conflicts, topology, ledger claims, preservation claims, and index state reviewed; material preservation loss found
- **AC-2: PASS:** every `make check` failure class and exact disposition recorded
- **AC-3: PASS:** checksum-pinned non-container Rust path defined without reducing the workflow matrix
- **AC-4: PASS:** exact npm package, advisories, dependency class, fixability, and pre-commit disposition recorded
- **AC-5: PASS:** three normalizations attributed and exact worktree instructions plus reject verdict recorded

## Documentation Impact

No steady-state product or architecture document changes are required for this investigation. Existing architecture and preservation documents must be corrected by TASK-010 if final implementation differs from their current claims

## Open Risks

The merge remains open and uncommitted. This review made no source/test edit, staging change, commit, merge abort/reset, push, image build, registry action, host access, or deployment

## Recommended Next Step

Reopen TASK-010 for the original Developer and keep TASK-011 inactive until all blockers above are corrected and independently rereviewed

## Re-review 1 Findings

### Blocker: the staged tree returns 404 for every public LazyMCP route

Reopen 1 leaves `litellm/proxy/proxy_server.py` byte-identical to upstream for the conflicted route area and removes the fork's `root_lazymcp_route`, `dynamic_lazymcp_route`, and `toolset_lazymcp_route`. The replacement-equivalence claim in the conflict ledger is not true

`litellm/proxy/_lazy_features.py` registers the MCP sub-app only for requests beginning `/mcp` and mounts it at `/mcp`. It has no `/lazymcp` or `/toolset/{name}/lazymcp` feature. Inside the sub-app, `/` is mounted before `/lazymcp`, so those internal mounts do not establish the proxy-root public routes either

Independent command:

```bash
uv run --no-sync pytest -q tests/test_litellm/proxy/test_dynamic_mcp_route.py -k lazymcp
```

Result: six failures, 21 deselected. Every retained preservation case expected 200 and received 404 for:

- `/lazymcp`
- `/lazymcp/team-a`
- `/toolset/tools-a/lazymcp`
- The trailing-slash alias for each route

The Developer's focused evidence does not include `test_dynamic_mcp_route.py`, and the claimed 141-test LazyMCP admission/DCR run has no retained command log. This explains why the route regression escaped otherwise green `make check` and focused runs

Exact fix: restore these route owners in a module compatible with lazy loading, or add distinct lazy features that preserve the same observable contract. Cover exact `_original_path`, internal rewritten path, root/scoped/toolset dispatch, toolset admission before DB lookup, access-group fallback, trailing slash, 404, and safe 500 behavior. Do not rely on the current `/mcp` mount or add a broad `/` mount

### Other gates

- Exact-upstream `make check`: pass
- No budget limit increased versus either parent; several ceilings ratcheted down
- Rust 1.97.1 fmt, two clippy commands, and two test commands: pass; upstream's two credentialed live tests remain ignored
- Dashboard: 123 unit files/2,317 tests, 597 component files/6,394 tests, 52 integration files/512 tests, types/format/lint/knip/build pass; full and production audits report zero vulnerabilities
- Migration evidence reports 161 migrations on disposable empty PostgreSQL plus a no-pending second deploy
- Required CodeMaps are staged and `staticeng_validate` passes with zero warnings
- The three unrelated normalization files match `HEAD` exactly and are not staged
- Git has zero unmerged, unstaged, or untracked paths
- `git diff --cached --check` fails on trailing whitespace/blank EOF in two staged raw logs; sanitize or regenerate those evidence files before commit

### Re-review 1 Verdict

**REJECT / NO COMMIT.** TASK-010 AC-2, AC-3, AC-5, and AC-6 remain failed. Route preservation must be fixed and evidence corrected before source approval

## Re-review 2 Findings

### Blocker: LazyMCP discovery aliases are advertised but return 404

The dedicated `lazymcp_routes` feature correctly restores proxy-root transport routes, but its matcher is too broad. It claims any path ending `/lazymcp`, so the middleware loads `litellm.proxy.lazymcp_routes` for canonical protected-resource paths. Importing that module also imports MCP server/discovery modules as side effects, but the middleware marks only `lazymcp_routes` as registered. The authoritative `mcp_discoverable` router is not included before dispatch

The scoped alias `/lazymcp/{scope}/.well-known/oauth-protected-resource` is captured by `/lazymcp/{scope}` in the transport router itself. The toolset alias has the same first-load ownership collision through suffix matching

Independent cold-start probes returned:

- `/lazymcp/.well-known/oauth-protected-resource`: 404
- `/lazymcp/team-a/.well-known/oauth-protected-resource`: 404
- `/toolset/tools-a/lazymcp/.well-known/oauth-protected-resource`: 404

These paths are approved by the LazyMCP OAuth contract and are present in `discoverable_endpoints.py`. The generated OpenAPI and dashboard types advertise all three, so runtime and generated contracts disagree

Exact fix:

1. Route all canonical and alternate protected-resource paths through `mcp_discoverable` as the only discovery owner
2. Narrow `lazymcp_routes` matching to `/lazymcp[/]`, one scoped transport segment, and `/toolset/{name}/lazymcp[/]`; exclude `/.well-known/` forms explicitly
3. Ensure route precedence prevents `/lazymcp/{scope}` from consuming the alternate root metadata path
4. Prevent `_lazy_openapi_snapshot` from assigning side-effect discovery routes to the `lazymcp_routes` fragment or duplicating operation IDs
5. Add cold-start TestClient coverage for all six canonical/alternate root, scoped, and toolset metadata paths, including exact `resource` and authorization-server values

### Passing portions

- `uv run --no-sync pytest -q tests/test_litellm/proxy/test_dynamic_mcp_route.py -k lazymcp`: 11 passed
- `uv run --no-sync pytest -q tests/test_litellm/proxy/test_proxy_server.py -k lazymcp_lazy_feature`: six passed
- Root and trailing-slash transport probes return 204 without redirects; unknown scoped route returns exact 404; explicit toolset with unavailable DB returns 503
- Mapped LazyMCP evidence: 767 passed with eight warnings
- Exact-upstream `make check`: pass, generated 34 lazy fragments
- No budget limit increased against either merge parent
- Cached diff check, CodeMaps, and StaticEng validation pass
- Three unrelated normalization files still match `HEAD` and remain excluded
- Git has zero unmerged, unstaged, or untracked paths before Tech Lead review writes

### Re-review 2 Verdict

**REJECT / NO COMMIT.** TASK-010 AC-2, AC-3, AC-5, and AC-6 remain failed because discovery runtime and generated contracts diverge

## Re-review 3 Final Verdict

**PASS / COMMIT AUTHORIZED**

No blocking findings remain. Reopen 3 makes `mcp_discoverable` the sole owner of all six RFC 9728 LazyMCP discovery paths, keeps transport matching exact, and aligns runtime with generated OpenAPI/dashboard types

### Independent Verification

- Six separate cold-start proxy processes returned HTTP 200 and exact metadata for canonical/alternate root, scoped, and toolset discovery forms; only `mcp_discoverable` loaded
- Lazy matcher ownership assertions pass for all six discovery paths and all intended/rejected transport shapes
- OpenAPI assertions show all six discovery templates in `mcp_discoverable` and none in `lazymcp_routes`
- Direct transport/lazy rerun: 14 passed
- Discovery/OpenAPI rerun: seven passed
- Developer mapped suite: 1,123 passed with nine documented warnings
- Exact-upstream `make check`: pass
- Pinned Rust, complete dashboard/zero-audit, disposable migration, CodeMap, and StaticEng gates remain green
- No budget ceiling increased against either merge parent
- Cached diff check is clean, no unresolved entries exist, and the three unrelated normalizations match `HEAD` and remain excluded

### Acceptance Criteria

- **TASK-010 AC-1: PASS**
- **TASK-010 AC-2: PASS**
- **TASK-010 AC-3: PASS**
- **TASK-010 AC-4: PASS**
- **TASK-010 AC-5: PASS**
- **TASK-010 AC-6: PASS on authorized local merge commit**

### Residual Boundary

This approval covers source integration only. Candidate build, immutable image identity, SBOM/scans/signatures, real-service isolated smoke, push, publication, and deployment remain outside scope and require TASK-011/TASK-012 authorization

### Signed Verdict

[Agent Message] From: tech_lead To: product_manager

PASS. The reviewed staged merge is approved for local no-fast-forward commit. No push, build, publication, deployment, Fedora action, or NAS action is authorized or performed
