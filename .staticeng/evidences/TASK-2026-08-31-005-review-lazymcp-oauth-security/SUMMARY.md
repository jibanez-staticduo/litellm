# Security Review Summary

## Verdict

REJECT. Candidate construction is not authorized. Two high-severity protocol/security boundary defects and material verification gaps remain. The implementation task must be reopened for fixes and focused regressions before another review

## Ordered Findings

1. **HIGH: malformed case variants silently enter the legacy unscoped `/mcp` grant flow.** `is_lazymcp_resource_candidate()` performs a case-sensitive segment search, and `aggregate_authorize()` rejects parse failures only when that heuristic returns true (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:124`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:422`). Inputs such as `https://gateway.example/LazyMCP` and `https://gateway.example/toolset/name/LazyMCP` fail the exact parser but are not classified as LazyMCP candidates, so authorization continues with both resource bindings unset. Code and refresh redemption then preserve legacy permissive handling because both conflict functions return false for an unsealed resource (`litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:665`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:679`). This violates the approved requirement that malformed/case-variant LazyMCP resources fail with an OAuth error and mint no token; it can turn a malformed LazyMCP authorization attempt into a valid legacy `/mcp` credential
2. **HIGH: the canonical resource owner accepts public non-loopback HTTP and request-controlled authority.** `_trusted_base()` accepts `http` for every host (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:53`). When `PROXY_BASE_URL` is absent and the caller is not a trusted proxy, `get_request_base_url()` uses `request.base_url`, whose authority comes from the request Host header (`litellm/proxy/_experimental/mcp_server/oauth_utils.py:133`). Metadata, challenges, authorization binding, and admission therefore accept or emit an attacker-selected authority and non-loopback HTTP rather than enforcing the SCR's trusted-origin, hostile-Host rejection, and production-HTTPS boundary. No implementation test exercises hostile Host/forwarded headers, trusted external base, or the loopback-only HTTP exception (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:15`)
3. **MEDIUM: not every LazyMCP 401 receives the required resource-specific Bearer challenge.** The new challenge conversion exists only in `_admission_failure_fallback()` and gateway-session branches (`litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:261`, `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:275`, `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:827`). The explicit `x-litellm-api-key` branch calls `user_api_key_auth()` directly and lets its 401 escape without LazyMCP challenge conversion (`litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:393`, `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:436`). This contradicts the unconditional challenge rule for supported LazyMCP transports
4. **MEDIUM: security-sensitive tests are too narrow to establish mutation-sensitive coverage.** Admission has one scoped mismatch test only (`tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py:8430`); it does not cover aggregate/toolset success and replay, legacy-token rejection on all three resources, no-token and invalid-token challenge matrices, selection-header invariance, or explicit-key 401 behavior. DCR coverage uses one mismatch for each parameterized happy-path resource but omits malformed case variants, foreign origins, percent encodings, rewritten `/mcp`, two-scope/toolset replay, and refresh missing-resource cases (`tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:908`). The parser/route test omits root paths, trusted proxy behavior, hostile headers, route collisions, and HTTPS policy (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:29`)
5. **MEDIUM: original-path preservation is implemented but not regression-tested at the three route owners.** The runtime writes `_original_path` in aggregate, scoped, and toolset routes (`litellm/proxy/proxy_server.py:17454`, `litellm/proxy/proxy_server.py:17624`, `litellm/proxy/proxy_server.py:17657`), while the mapped route suite only asserts this behavior for an unrelated `/mcp` route (`tests/test_litellm/proxy/test_dynamic_mcp_route.py:577`). A mutation deleting any new assignment can make admission derive the rewritten route and break exact audience enforcement without a route-level regression failing

## Acceptance Criteria Coverage

- **AC-1: FAIL.** The parser is conservative for many forms but does not enforce HTTPS/loopback policy or trusted authority, and tests do not cover the required proxy/root/host matrix
- **AC-2: FAIL.** Exact admission is correctly placed before user reload, and code/access/refresh claims preserve the resource, but malformed case variants can bypass strict LazyMCP flow classification and mint an unscoped legacy token
- **AC-3: FAIL.** Metadata is generic and explicit route ordering is sound, but challenge coverage is incomplete and preservation/root/proxy behavior is insufficiently verified
- **AC-4: FAIL.** Existing focused and mapped suites pass, but the missing negative matrices and route-owner assertions leave straightforward security mutations alive
- **AC-5: PASS.** Findings are ordered with file/line references; the review verdict is REJECT

## Candidate Isolation Decision

The current shared worktree must not be used directly as a Docker build context. It contains unrelated modified LLM transformation/runtime files, unrelated tests, broad untracked CodeMaps, and unrelated StaticEng state. After the findings are fixed and re-reviewed, isolation is technically feasible by creating a clean detached worktree at the explicitly recorded base revision, applying a reviewed patch manifest containing only the LazyMCP task hunks, adding only the task's new parser/test files and required architecture document, and confirming `git status --short` plus `git diff --name-status` against that manifest before building. A blanket working-tree copy, `git diff` over all paths, or inclusion of all untracked CodeMaps is not acceptable

## Evidence Reviewed

Reviewed the approved SCR, architecture handoff, implementation task, architecture contract, task-owned runtime/test diff, focused result (113 passed), mapped result (1042 passed), lint result, type-check result, StaticEng note, and Docker-blocker note. `git diff --check` passed. `staticeng_validate` remains blocked by the repository's pre-existing broad missing-CodeMap inventory, beginning with `litellm/llms/gradient_ai`, `litellm/llms/novita`, and `litellm/llms/llamafile`; this investigation did not repair unrelated orchestration state. No implementation or test file was edited by this review

## Documentation Impact

The steady-state architecture contract exists and covers the intended behavior, but it currently overstates enforcement of HTTPS, trusted public authority, complete challenge behavior, and test-backed admission guarantees. Product documentation remains unnecessary. The architecture contract should be corrected only through the reopened implementation/documentation closure after runtime behavior is fixed

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

Security review rejects the implementation and does not authorize candidate construction. Reopen the implementation task for the malformed-resource classification, trusted-origin/HTTPS enforcement, complete LazyMCP challenge handling, and the missing negative/route-preservation regressions. After fixes pass review, construct the candidate only in a clean detached worktree using an explicit task-owned patch manifest

## Reopen 1 Security Re-review

### Ordered Findings

1. **HIGH: an invalid non-empty `PROXY_BASE_URL` re-enables untrusted Host authority.** `_trusted_base()` decides that a configured authority exists from the raw non-empty environment value (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:77`), but `get_request_base_url()` independently rejects an invalid configured value and falls back to the request base URL (`litellm/proxy/_experimental/mcp_server/oauth_utils.py:113`, `litellm/proxy/_experimental/mcp_server/oauth_utils.py:143`). With `PROXY_BASE_URL=not-a-valid-url`, an untrusted request using `Host: attacker.example` is therefore accepted as `https://attacker.example/lazymcp`. The trust decision and selected base do not share one validated source, so a configuration typo converts hostile Host input into canonical metadata, challenges, OAuth bindings, and admission audiences
2. **HIGH: a remote untrusted request can select a loopback authority through Host.** `_trusted_base()` treats the selected hostname alone as proof of local development (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:69`, `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:79`). It does not require the request peer to be loopback. With no configured base and no trusted proxy, a remote peer can send `Host: localhost` and have `https://localhost/lazymcp` accepted. This contradicts the documented rule that untrusted Host cannot select authority and makes the local-development exception depend on attacker-controlled authority rather than a literal loopback connection
3. **HIGH: the malformed-resource classifier now breaks preserved legacy `/mcp` flows.** `is_lazymcp_resource_candidate()` returns true whenever the substring `lazymcp` appears anywhere in the entire candidate URL (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:150`). `aggregate_authorize()` maps any such value that is not a canonical LazyMCP resource to `invalid_target` (`litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:422`). A valid legacy resource such as `https://lazymcp.example/mcp`, a per-server resource whose identifier contains `lazymcp`, or an otherwise legacy URL carrying that text outside a LazyMCP path shape is now rejected. This violates the approved requirement that `/mcp` and per-server DCR behavior remain unchanged. The classifier must recognize malformed variants of the three LazyMCP path families without using an unrestricted whole-URL substring fallback

### Resolved Prior Findings

- **Malformed case/encoding fallback: RESOLVED for intended LazyMCP shapes.** Case-varied, encoded, foreign-origin, query-bearing, cross-kind, and two-scope authorization/redemption cases now fail closed, and tests assert no flow cookie is created (`tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:944`)
- **Complete challenges: RESOLVED.** Explicit-key failures are converted, all three resource forms cover no-token and invalid-token behavior, selection headers are invariant, and legacy unscoped sessions fail on each LazyMCP route (`litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:437`, `tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py:8519`)
- **Security matrices: RESOLVED for the prior requested audience/challenge cases.** Aggregate, scoped, toolset, cross-kind, missing-resource refresh, hostile forwarded header, root-path, and HTTPS cases now have focused regressions
- **Original-path route regressions: RESOLVED.** Aggregate, scoped, toolset, and trailing-slash aliases assert both retained public path and expected internal rewrite (`tests/test_litellm/proxy/test_dynamic_mcp_route.py:620`)

### Verdict

REJECT. Candidate construction is not authorized. The trust-source bypasses affect every metadata, challenge, authorization, and admission URL, and the classifier introduces a preservation regression on legacy OAuth resources

### Acceptance Criteria Coverage

- **AC-1: FAIL.** Accepted/rejected forms are substantially improved, but untrusted authority remains accepted through invalid configuration and remote loopback Host spoofing
- **AC-2: PASS for exact LazyMCP artifact binding and admission ordering.** Code/access/refresh persistence and pre-reload exact audience enforcement are covered; candidate construction still fails the overall security gate because authority selection is unsafe
- **AC-3: FAIL overall.** Metadata genericity, challenges, route ordering, split ownership, and original-path preservation pass, but the overbroad classifier regresses preserved legacy `/mcp` and per-server authorization behavior
- **AC-4: PASS for the prior missing security matrices.** New regression gaps remain for invalid configured base, remote loopback Host spoofing, and legacy URLs containing `lazymcp` outside a LazyMCP path shape
- **AC-5: PASS.** Reopen findings are ordered with exact references and an explicit REJECT verdict

### Independent Verification

- Independently ran the bounded LazyMCP parser, DCR, admission, and route-owner selection: 37 passed, 409 deselected, no failures
- Independently ran Ruff over the task-owned Python paths excluding unrelated dirty `proxy_server.py`: all checks passed
- `git diff --check` passed for the task-owned runtime/test path set
- Direct probes reproduced both authority bypasses: a remote request with `Host: localhost` was accepted, and invalid non-empty `PROXY_BASE_URL` allowed `Host: attacker.example`
- Developer evidence reports 163 focused and 1067 mapped tests passing, plus zero-error focused basedpyright
- `staticeng_validate` remains blocked by the pre-existing broad missing-CodeMap inventory and was not repaired by this investigation

### Candidate-build Decision

No task-owned patch manifest is authorized while the verdict is REJECT. The dirty shared worktree remains prohibited as a build context. After the remaining fixes pass re-review, the previously defined clean detached-worktree strategy can be finalized with an exact base revision, path/hunk manifest, new-file checksums, and a post-application diff allowlist

### Documentation Impact

The updated architecture contract correctly states the intended trust policy, but runtime does not yet enforce it in the invalid-configuration and remote-loopback-Host cases. No product documentation change is required

### Signed Reopen Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen 1 remains REJECTED and candidate construction is unauthorized. The prior malformed-shape, challenge, matrix, and original-path gaps are fixed, but trusted authority can still be bypassed and the whole-URL LazyMCP substring classifier regresses preserved legacy OAuth resources

## Reopen 2 Security Re-review

### Ordered Findings

1. **HIGH: slash-containing legacy per-server resources whose final identifier segment is exactly `lazymcp` are still rejected.** The classifier skips `lazymcp` only when its immediately preceding segment is `mcp` (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:182`). For the supported slash-containing server-name shape `/mcp/team/lazymcp`, the preceding segment is `team`, `remaining == 1`, and the function returns true (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:185`, `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:188`). `aggregate_authorize()` then returns `invalid_target` because the strict LazyMCP parser correctly rejects that legacy shape (`litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:422`). Existing legacy parsing explicitly supports server names containing one slash (`litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:641`). The new regression set covers `/mcp/lazymcp-server` but not `/mcp/team/lazymcp` (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:88`, `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:1037`). This leaves the Reopen 1 preservation finding partially unresolved

### Resolved Reopen 1 Findings

- **Invalid configured base fallback: RESOLVED.** `_trusted_base()` validates a non-empty configured base before calling the fallback-capable shared resolver and fails closed on invalid configuration (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:87`)
- **Remote loopback Host spoofing: RESOLVED.** The local-development exception now requires both loopback authority and loopback request peer, for HTTP and HTTPS (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:97`, `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:104`)
- **Legacy classifier preservation: PARTIAL.** Authorities, queries, and simple `/mcp/lazymcp-server` identifiers are preserved, but multi-segment legacy server identifiers ending in exact `lazymcp` remain misclassified

### Verdict

REJECT. Candidate construction is not authorized. One high-severity preservation regression remains in the exact boundary under review

### Acceptance Criteria Coverage

- **AC-1: PASS.** Trusted authority, HTTPS, loopback peer, canonical parser, and malformed intended LazyMCP forms now satisfy the reviewed boundary
- **AC-2: PASS.** Exact code/access/refresh binding and admission ordering remain correct and unchanged
- **AC-3: FAIL.** Metadata, challenges, route ordering, split ownership, and original-path behavior pass, but legacy per-server DCR preservation still regresses for a supported identifier shape
- **AC-4: FAIL.** Logs 13 through 16 pass, but the preservation tests omit the exact slash-containing legacy identifier that exposes the remaining classifier defect
- **AC-5: PASS.** The remaining finding is ordered with exact references and an explicit REJECT verdict

### Independent Verification

- Reviewed implementation evidence logs 13 through 16: 169 focused tests passed, 1069 mapped tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran the three Reopen 2 regression groups: 7 passed, 72 deselected, no failures
- Direct classifier probe returned true for `https://gateway.example/mcp/team/lazymcp`, confirming the uncovered legacy preservation regression
- `git diff --check` remains clean for the task-owned runtime/test path set from the prior review; no implementation or test file was edited

### Candidate-build Decision

No candidate build or exact patch manifest is authorized while the verdict is REJECT. Continue to prohibit the dirty shared worktree as a Docker context. After the final preservation fix passes bounded review, candidate construction may use the clean detached-worktree procedure previously specified, with the exact task-owned path list frozen at that review

### Documentation Impact

The architecture contract remains correct as intended steady-state documentation. Runtime still has one legacy preservation mismatch; no product documentation update is required

### Signed Reopen 2 Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen 2 remains REJECTED and candidate construction is unauthorized. Trusted-base fixes pass, but `/mcp/team/lazymcp` demonstrates that the classifier still rejects a supported slash-containing legacy per-server resource

## Reopen 3 Security Re-review

### Ordered Findings

1. **HIGH: the legacy-preservation rule reopens malformed LazyMCP fallback when the trusted root path is `/mcp`.** `is_lazymcp_resource_candidate()` now ignores every `lazymcp` segment whenever any earlier path segment equals `mcp` (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:182`, `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:188`). That fixes the root-mounted legacy resource `/mcp/team/lazymcp`, but the classifier has no request or trusted-root context. With `PROXY_BASE_URL=https://gateway.example/mcp`, the canonical aggregate LazyMCP family is rooted at `https://gateway.example/mcp/lazymcp`; a malformed case variant `https://gateway.example/mcp/LazyMCP` correctly fails strict parsing but the classifier returns false because of the root's `mcp` segment. `aggregate_authorize()` therefore does not return `invalid_target` and can create an unscoped legacy connect flow (`litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:422`). Existing tests prove valid non-empty-root parsing but do not cover malformed authorization under a root whose segment collides with the legacy namespace. The classifier decision must account for the trusted root/request rather than treating every preceding `mcp` segment as legacy

### Confirmed Fixes

- **Exact `/mcp/team/lazymcp` preservation: PASS for a root-mounted proxy.** Classifier/parser assertions and real aggregate authorization prove the resource remains unscoped legacy (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:88`, `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:1037`)
- **Trusted authority: PASS.** Invalid configured base fails closed, remote peers cannot claim loopback authority, trusted proxy/root handling remains covered, and non-loopback HTTP remains rejected
- **Audience controls: PASS.** Exact code/access/refresh persistence, cross-resource rejection, legacy-token rejection, and pre-reload exact admission remain unchanged and covered

### Verdict

REJECT. Candidate construction is not authorized. The exact requested legacy case passes, but the fix creates a high-severity malformed-resource fallback at a supported non-empty trusted root

### Acceptance Criteria Coverage

- **AC-1: FAIL.** Canonical parsing is correct, but malformed intended LazyMCP forms do not fail closed for every supported root path
- **AC-2: PASS.** Exact code/access/refresh binding and admission ordering remain intact
- **AC-3: FAIL overall.** Metadata, challenges, route ordering, preservation, and split ownership pass for tested roots, but authorization classification is not root-aware
- **AC-4: FAIL.** Logs 17 through 20 pass, but no mutation-sensitive DCR regression combines non-empty `/mcp` root with malformed/case-varied LazyMCP input
- **AC-5: PASS.** The finding is ordered with exact references and an explicit REJECT verdict

### Independent Verification

- Reviewed logs 17 through 20: 171 focused tests passed, 783 bounded mapped tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran exact legacy, classifier, authority, and audience-focused selections: 12 passed, 69 deselected, no failures
- Direct probe with `PROXY_BASE_URL=https://gateway.example/mcp` confirmed `https://gateway.example/mcp/LazyMCP` fails strict parsing while `is_lazymcp_resource_candidate()` returns false
- `git diff --check` passed for the task-owned tracked runtime/test set; no implementation or test file was edited

### Candidate-build Decision

No isolated candidate or exact task-owned patch manifest is authorized while the verdict is REJECT. The dirty shared worktree remains prohibited as a Docker context. Candidate construction must wait for a request/root-aware classifier fix and one final bounded approval

### Documentation Impact

The architecture contract remains correct as intended steady-state documentation. Runtime still violates its malformed-resource rule at the `/mcp` trusted-root collision; no product documentation update is required

### Signed Reopen 3 Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen 3 remains REJECTED and candidate construction is unauthorized. `/mcp/team/lazymcp` is preserved and prior authority/audience fixes remain intact, but a trusted root of `/mcp` lets malformed `{root}/LazyMCP` bypass strict authorization classification

## Reopen 4 Final Security Review

### Ordered Findings

No blocking findings

### Confirmed Closed Findings

- **Trusted-root classification: CLOSED.** `is_lazymcp_resource_candidate()` receives the request, obtains the validated trusted root, strips only that root, and recognizes only the three intended relative LazyMCP path families (`litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py:176`). `aggregate_authorize()` uses that request-aware result before creating a connect flow (`litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:422`)
- **Root collision and malformed resources: CLOSED.** With `PROXY_BASE_URL=https://llm.example.com/mcp`, `/mcp/LazyMCP` is classified relative to the trusted root and returns `invalid_target` with no cookie (`tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:967`)
- **Legacy preservation: CLOSED.** In a root-mounted deployment, `/mcp/team/lazymcp` remains a legacy resource and creates an unscoped legacy flow (`tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:1047`)
- **Trusted authority and HTTPS: CLOSED.** Invalid configured bases fail closed, remote peers cannot claim loopback authority, untrusted Host/forwarded headers cannot select authority, trusted proxy/root handling remains explicit, and public non-loopback HTTP remains rejected
- **Challenges and audience: CLOSED.** Missing/invalid/explicit-key LazyMCP 401s advertise exact path-inserted metadata independent of selection headers; code/access/refresh artifacts preserve one exact resource; cross-resource replay and legacy unscoped sessions fail; admission checks audience before user reload
- **Preservation and route ownership: CLOSED.** Aggregate, scoped, toolset, and trailing-slash route owners retain `_original_path`; existing `/mcp`, permissions, selection, and upstream-auth behavior remain covered by mapped regressions

### Verdict

PASS. The candidate build is authorized under the exact isolation constraints below. This is authorization to construct and smoke an immutable candidate only; it is not deployment or production-mutation approval

### Acceptance Criteria Coverage

- **AC-1: PASS.** Canonical forms, malformed/case/encoding forms, trusted authority, HTTPS, loopback peer, proxy, and root-relative classification were reviewed
- **AC-2: PASS.** Code/access/refresh binding and pre-reload exact audience admission are fail closed and mutation-sensitive
- **AC-3: PASS.** Generic metadata, exact challenges, route ordering, split ownership, original-path preservation, and legacy boundaries are covered
- **AC-4: PASS.** Focused security matrices and bounded mapped regressions cover all prior findings and the trusted-root collision
- **AC-5: PASS.** No blocking findings remain; explicit PASS and candidate authorization are recorded

### Independent Verification

- Reviewed logs 21 through 24: 173 focused tests passed, 784 bounded mapped tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran classifier, trusted authority, malformed authorization, legacy preservation, challenge, audience, and route-owner selections: 32 passed, 424 deselected, no failures
- Reviewed the exact request-aware classifier and authorization call site; `git diff --check` passed for the tracked candidate runtime/test path set
- No implementation or test file was edited during review
- Global `staticeng_validate` remains outside candidate scope due to the repository's pre-existing broad missing-CodeMap inventory; candidate smoke must record this known external debt without importing unrelated CodeMaps

### Authorized Candidate Runtime Manifest

Base revision: `9af49e5b34e25cdc9ad40f9bb50a178f40320417`

Reviewed source fingerprints at authorization time:

- Six tracked-path binary patch SHA-256: `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`
- New parser file SHA-256: `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`

Apply exactly these seven runtime paths and no other dirty-worktree changes:

1. `gateway/routes/allowlist.py`
2. `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py`
3. `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py`
4. `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py`
5. `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py` (new file)
6. `litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py`
7. `litellm/proxy/proxy_server.py`

Tests, architecture/task/evidence documents, and CodeMaps are verification/closure artifacts, not candidate image source mutations. Do not copy them into the detached build tree. In particular, do not include unrelated modified LLM transformation files, unrelated tests, repository-wide untracked CodeMaps, or unrelated StaticEng state

### Detached-worktree Procedure

Use an external staging directory under `/tmp/opencode`; do not build from the shared workspace:

```bash
SRC=/home/staticduo/git/litellm
BASE=9af49e5b34e25cdc9ad40f9bb50a178f40320417
STAGE=/tmp/opencode/lazymcp-oauth-candidate
WT="$STAGE/worktree"
PATCH="$STAGE/runtime-tracked.patch"

mkdir -p "$STAGE"
git -C "$SRC" diff --binary "$BASE" -- \
  gateway/routes/allowlist.py \
  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py \
  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py \
  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py \
  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py \
  litellm/proxy/proxy_server.py > "$PATCH"

git -C "$SRC" worktree add --detach "$WT" "$BASE"
git -C "$WT" apply --check "$PATCH"
git -C "$WT" apply "$PATCH"
install -D -m 0644 \
  "$SRC/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py" \
  "$WT/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py"
```

Before building, independently enforce the exact manifest. The following script must print `manifest-ok`; any extra path aborts construction:

```bash
WT="$WT" python - <<'PY'
import os
import subprocess

expected = {
    "gateway/routes/allowlist.py",
    "litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py",
    "litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py",
    "litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py",
    "litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py",
    "litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py",
    "litellm/proxy/proxy_server.py",
}
wt = os.environ["WT"]
raw = subprocess.check_output(
    ["git", "-C", wt, "status", "--porcelain=v1", "--untracked-files=all"],
    text=True,
)
actual = {line[3:] for line in raw.splitlines() if line}
if actual != expected:
    raise SystemExit(f"manifest mismatch: extra={sorted(actual - expected)} missing={sorted(expected - actual)}")
print("manifest-ok")
PY

git -C "$WT" diff --check
cmp \
  "$SRC/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py" \
  "$WT/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py"
test "$(sha256sum "$PATCH" | cut -d' ' -f1)" = \
  "6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557"
test "$(sha256sum "$WT/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py" | cut -d' ' -f1)" = \
  "b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462"
```

Then build an immutable candidate from `"$WT"`, record the image ID/digest and patch/new-file checksums, and perform the SCR's secret-free readiness, six discovery aliases, exact 401, authorized initialize/tool call, reconnect, `/mcp`, MCP REST, and upstream integration smoke checks. Do not tag as production, replace/restart the production container, or reuse the shared worktree as context. Remove the detached worktree only after evidence is captured:

```bash
docker build --pull=false -t litellm:lazymcp-oauth-candidate "$WT"
docker image inspect --format '{{.Id}}' litellm:lazymcp-oauth-candidate
sha256sum "$PATCH" \
  "$WT/litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py"
# Run the approved isolated smoke procedure and write logs before cleanup.
git -C "$SRC" worktree remove "$WT"
```

### Documentation Impact

The architecture contract now matches reviewed runtime behavior. No product documentation change is required. Candidate build/smoke evidence remains outstanding under implementation AC-8

### Signed Reopen 4 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. All security findings are closed. Candidate construction is authorized only from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` using the exact seven-path runtime manifest and detached-worktree procedure above; deployment and production mutation remain unauthorized pending build, smoke, and PMA closure

## Reopen 5 Test-only and Retained-image Review

### Ordered Findings

No blocking findings

### Review Results

- **Runtime and candidate inputs: UNCHANGED.** The six-path application patch remains `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`; the parser remains `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`; the authorized Dockerfile remains `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`; and the retained amd64 image is still present as `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf`. Reopen 5 adds no runtime, Dockerfile, lock, Cargo, or image input
- **Discovery fail-closed coverage: PASS.** A real FastAPI router under HTTP with non-loopback Docker peer `172.18.0.2`, no `PROXY_BASE_URL`, and request-controlled internal Host asserts generic 404 for all six aliases (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:239`)
- **Discovery configured-success coverage: PASS.** The same Docker-style peer with reserved `PROXY_BASE_URL=https://candidate.invalid` asserts HTTP 200, exact aggregate/scoped/toolset resources, both aliases per shape, and exact authorization server (`tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py:263`)
- **Challenge fail-closed/configured-success coverage: PASS.** Aggregate, scoped, and toolset scopes prove `_lazymcp_challenge()` returns `None` without a trusted base rather than deriving authority from Host, then emits exact configured path-inserted metadata with `invalid_token` under the reserved HTTPS base (`tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py:8567`)
- **TASK-015 diagnosis alignment: PASS.** Tests exercise the diagnosed handler boundary, not synthetic route presence alone: registered discovery handlers deliberately return 404 when trust cannot be established, while challenge construction deliberately declines to fabricate an authority. No trust-policy weakening is introduced

### Verdict

PASS. Retained-image re-smoke is authorized without rebuild under the exact constraints below. This is not promotion, deployment, or production-mutation approval

### Independent Verification

- Reviewed logs 25 through 28: 35 focused tests passed, 710 bounded mapped tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran the exact new discovery and challenge regressions: 3 passed, 362 deselected, no failures
- `git diff --check` passed for both test files
- Independently recomputed the application patch, parser, and Dockerfile fingerprints and inspected the retained image ID/architecture; all match the frozen candidate provenance
- No implementation or test file was edited during review

### Retained-image Re-smoke Authorization

Authorized immutable image:

`sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` (`linux/amd64`)

Required smoke-only public identity:

`PROXY_BASE_URL=https://candidate.invalid`

The value is reserved, non-secret, HTTPS, and valid only as the isolated candidate's asserted external identity. Do not change the image, rebuild it, mount the shared worktree, inject production configuration, mount a production database, or use production credentials. Abort if `docker image inspect` does not return the exact image ID and amd64 architecture

Run the retained image with its normal entrypoint in a new isolated disposable network/container, passing only the existing secret-free candidate settings plus `PROXY_BASE_URL=https://candidate.invalid`. Requests may reach the container through its local HTTP test port, but every metadata `resource`, `authorization_servers`, and `WWW-Authenticate resource_metadata` assertion must use the configured HTTPS authority, never the Docker Host or forwarded headers

The re-smoke must record:

1. Exact retained image ID/architecture and pre-smoke production container ID, image ID, status, and readiness
2. All six discovery aliases returning 200 with exact aggregate, scoped, and toolset metadata rooted at `https://candidate.invalid`
3. Aggregate, scoped, and toolset no-token and invalid-token responses carrying exact path-inserted `resource_metadata` rooted at `https://candidate.invalid`; selection headers must not alter the challenge
4. Reconnect loop with zero discovery 404s
5. Readiness, `/mcp`, MCP REST, management tool-list, and upstream-preservation checks from TASK-006 Reopen 4
6. Authorized initialize/tool behavior where possible without production credentials; retain the existing explicit environment-bound BLOCKED disposition if the isolated database-free setup cannot perform it
7. Post-smoke production invariants and complete removal of the disposable container/network/worktree, while retaining the immutable image for evidence

Do not claim promotion success from this re-smoke alone. Signature/attestation, aggregate SBOM, comparative vulnerability scanners, and any credential-dependent protocol gate remain independently fail closed as already recorded by TASK-006/TASK-015

### Documentation Impact

No product or architecture documentation change is required. TASK-015's smoke-contract guidance should govern the TASK-006 evidence update: record presence and expected public authority only, never environment dumps or secrets

### Signed Reopen 5 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Reopen 5 is test/evidence-only and all frozen runtime/image inputs remain unchanged. Retained-image re-smoke is authorized without rebuild using reserved `PROXY_BASE_URL=https://candidate.invalid`, exact HTTPS metadata/challenge assertions, full prior preservation gates, production invariants, and cleanup. Deployment remains unauthorized

## Reopen 6 TASK-016 Security Review

### Ordered Findings

1. **HIGH: intentionally anonymous admission bypasses explicit toolset resolution and authorization.** `_prepare_mcp_request_context()` reads the server-owned toolset name after shared admission, but resolves that name only when `user_api_key_auth is not None` (`litellm/proxy/_experimental/mcp_server/server.py:4401`, `litellm/proxy/_experimental/mcp_server/server.py:4404`). It likewise applies `_apply_toolset_scope()` only when both an ID and non-None auth exist (`litellm/proxy/_experimental/mcp_server/server.py:4415`). An installation whose configured admission policy intentionally succeeds anonymously can return `user_api_key_auth=None`; the explicit `/toolset/{name}/lazymcp` request then skips the database-down 503, unknown 404, and toolset authorization boundary and continues as unscoped LazyMCP. TASK-016 explicitly requires anonymous admission to continue into authenticated-phase database/toolset outcomes rather than forcing a 401 (`.staticeng/tasks/todo/TASK-2026-08-31-016-fix-toolset-challenge-order.md:73`). The architecture contract also says the handler resolves and authorizes after admission without excluding anonymous success (`.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md:15`). An independent direct probe returned successfully with zero lookup calls when admission returned `None`, confirming the bypass
2. **MEDIUM: ContextVar lifecycle/concurrency coverage does not meet TASK-016's mutation-sensitive requirement.** The route correctly sets the name token and resets it in `finally` (`litellm/proxy/proxy_server.py:17447`, `litellm/proxy/proxy_server.py:17450`), and `_stream_mcp_asgi_response()` creates a child task that copies request context (`litellm/proxy/proxy_server.py:17329`, `litellm/proxy/proxy_server.py:17348`). The new route test verifies visibility and reset only after a successful response (`tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1198`). It does not verify reset when the streaming bridge raises or isolation between concurrent requests carrying different toolset names, even though TASK-016 requires success-and-exception reset and mutation-sensitive context leakage coverage (`.staticeng/tasks/todo/TASK-2026-08-31-016-fix-toolset-challenge-order.md:79`). The implementation appears structurally sound, but a future deletion/misplacement of `finally` or incorrect task-context handling is not adequately guarded

### Confirmed Correct Boundaries

- **Admission ordering and exact challenges: PASS.** The explicit route no longer touches Prisma/catalog state; it preserves `_original_path`, rewrites only the internal path, and enters shared admission. Missing and invalid credentials receive the exact toolset metadata challenge, and lookup is asserted not awaited (`litellm/proxy/proxy_server.py:17443`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1357`)
- **Non-enumeration for rejected admission: PASS.** Missing/invalid credentials terminate before database/name lookup, so known, unknown, and unavailable states are indistinguishable to rejected callers
- **Authenticated outcomes: PASS for covered states.** After non-None authenticated admission, absent Prisma returns 503, unknown name returns 404, and a known name resolves once and applies scope once (`tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1662`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1708`)
- **Legacy toolset and permission implementation: PRESERVED by inspection.** Existing ID ContextVar paths remain unchanged, inbound `x-mcp-toolset-id` is stripped, simultaneous name+ID fails closed, and `_apply_toolset_scope()` retains no-server, admin, explicit grant, permission-resolution, and scoped-object behavior (`litellm/proxy/_experimental/mcp_server/server.py:4398`, `litellm/proxy/_experimental/mcp_server/server.py:4402`, `litellm/proxy/_experimental/mcp_server/server.py:4437`)

### Verdict

REJECT. Do not freeze or build a new candidate. The anonymous-admission bypass can broaden explicit toolset behavior, and required lifecycle/concurrency regressions are incomplete

### Acceptance Criteria Coverage

- **AC-1: PASS.** Admission ordering, public path preservation, internal rewrite, and exact challenges were reviewed
- **AC-2: FAIL.** Non-enumeration holds for rejected credentials but anonymous successful admission bypasses catalog and authorization boundaries
- **AC-3: FAIL overall.** Authenticated DB-down/unknown/permitted semantics pass; anonymous semantics violate TASK-016, and an explicit new unauthorized route test is absent even though the existing scope function remains fail closed
- **AC-4: FAIL.** Context reset/concurrency and anonymous-policy mutations are not covered
- **AC-5: PASS.** Findings are ordered with exact references and an explicit REJECT verdict

### Independent Verification

- Reviewed logs 29 through 32: 9 focused tests passed, 335 mapped route/toolset/auth tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran bounded toolset LazyMCP, challenge/audience, and legacy toolset selections: 6 passed, 659 deselected, no failures
- Directly invoked `_prepare_mcp_request_context()` with the explicit name ContextVar and a successful anonymous admission result; it returned `user_api_key_auth=None` and awaited the toolset lookup zero times
- Reviewed the exact route, streaming bridge, context owner, post-admission resolver, scope function, architecture contract, and TASK-016 state table
- No implementation or test file was edited during review

### Candidate Decision

No newly frozen manifest is authorized. The retained image is obsolete for TASK-016 because `server.py` and `proxy_server.py` runtime behavior changed, but the replacement runtime set must not be frozen until the findings pass re-review. Preserve the current Dockerfile/application inputs without rebuild in the interim

### Documentation Impact

The architecture contract states the intended ordering correctly; runtime does not satisfy it for anonymous successful admission. No product documentation change is required. After correction, the candidate manifest must include `litellm/proxy/_experimental/mcp_server/server.py` in addition to the previously frozen runtime/Dockerfile inputs

### Signed Reopen 6 Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT. Missing/invalid toolset challenges and authenticated resolution ordering are corrected, but anonymous successful admission bypasses name resolution and scope enforcement. Add anonymous-policy plus exception/concurrency ContextVar regressions and return for review before any server.py-inclusive candidate freeze

## Reopen 7 Final Toolset Security Review

### Ordered Findings

No blocking findings

### Confirmed Closed Findings

- **Anonymous admission: CLOSED.** Every explicit toolset request that completes admission resolves the name regardless of principal presence. Anonymous DB-down returns 503, unknown returns 404, and known returns explicit 403 before any unscoped continuation (`litellm/proxy/_experimental/mcp_server/server.py:4404`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1800`)
- **Authenticated authorization: CLOSED.** Known unauthorized principals receive 403 through `_apply_toolset_scope()`; permitted principals resolve once and apply scope once, preserving scoped permissions (`tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1758`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1846`)
- **Challenge ordering/non-enumeration: CLOSED.** Missing and invalid credentials terminate at shared admission with exact public toolset metadata before Prisma/name lookup, so DB-down, unknown, and known states are indistinguishable to rejected callers
- **Context lifecycle/concurrency: CLOSED.** Route-owned name context is visible during streaming and reset after success and exception; concurrent alpha/beta requests retain isolated names and leave the parent context empty (`tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1198`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1226`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1240`)
- **Double binding: CLOSED.** Simultaneous server-owned name and legacy ID contexts fail closed before lookup/scope (`litellm/proxy/_experimental/mcp_server/server.py:4402`, `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py:1881`)
- **Legacy behavior: PRESERVED.** Existing ID-context routes, inbound-header stripping, no-server sentinel, admin handling, explicit toolset grants, permission resolution, tool filtering, and scoped object construction remain unchanged

### Verdict

PASS. New isolated amd64 candidate construction is authorized under the frozen manifest and provenance below. This is build/smoke authorization only, not promotion or deployment approval

### Acceptance Criteria Coverage

- **AC-1: PASS.** Anonymous, authenticated, DB-down, unknown, unauthorized, permitted, challenge ordering, and non-enumeration outcomes were reviewed
- **AC-2: PASS.** Public-path-derived audience/challenges remain independent of catalog state and admission precedes all toolset lookup
- **AC-3: PASS.** Context ownership, reset, child-task copying, concurrent isolation, and double-binding failure are covered
- **AC-4: PASS.** Existing legacy toolset permission and routing behavior remain covered by mapped suites
- **AC-5: PASS.** No blocking findings remain; explicit PASS and candidate authorization are recorded

### Independent Verification

- Reviewed logs 33 through 36: 16 focused tests passed, 342 mapped route/toolset/auth tests passed, Ruff passed, and focused basedpyright reported zero errors
- Independently reran bounded explicit-toolset, anonymous, challenge/audience, and legacy toolset selections: 6 passed, 666 deselected, no failures
- Reviewed exact runtime, tests, architecture contract, and the frozen candidate source inputs; `git diff --check` passed
- No implementation or test file was edited during review

### Frozen Candidate Authorization

Base revision: `9af49e5b34e25cdc9ad40f9bb50a178f40320417`

Platform: `linux/amd64` only. Arm64 remains unauthorized

Ordered nine-path manifest:

```text
9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d  Dockerfile
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
393408f57980abb4f8375786d81e1e73fb787f413545829c9757520a921d1b0f  litellm/proxy/_experimental/mcp_server/server.py
08a60623520e888168b40d7fc3d83b6954d08e39b77b0ab5b6c770fcd9e07ed8  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

- Ordered manifest SHA-256: `2354fef3fc6317918da927f062e19a808e333f28b8c958c7fc07ab7b186359bf`
- Seven tracked application-path patch SHA-256, including `server.py`: `a21069c21ded766dd401df0b125385bf9e07898157a89f55bd103504a9f2d49b`
- Dockerfile plus seven tracked application paths patch SHA-256: `1e926f0c5f74f84177f4899e8757703f5e6efc6c630ffc04f53dc935ab911ff3`
- New parser SHA-256: `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`

Supplementary immutable build inputs:

```text
3b8240e1f70307caf0c1641639577060eda2d7070b8962a008f91dc949b12117  pyproject.toml
a7cc57875c67de85bbae0f82b834f31fc9d0c029073ef29e0883787a31a985e8  uv.lock
65cb1ec9ed32ebc0f450c0649a03159943a1f21625f61f1c993448b2ff60b83a  litellm-rust/Cargo.toml
ef6ae9d1e34b0bf82d93f06a3ef62694a1489a2a890b3cadecdbd74120e2273d  litellm-rust/Cargo.lock
```

Pinned OCI provenance remains unchanged from TASK-014:

- Wolfi build/runtime index: `cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`; required amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`
- uv index: `ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a`; required amd64 child `sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8`
- Rust index: `docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`; required amd64 child `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`
- UI index: `docker.io/library/node:24.19-alpine3.24@sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43`; required amd64 child `sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43`

### Build and Smoke Constraints

Construct a clean detached worktree under `/tmp/opencode` from the frozen base. Generate one binary patch from exactly `Dockerfile` plus the seven tracked application paths, apply after `git apply --check`, and copy only the untracked parser. Require `git status --porcelain=v1 --untracked-files=all` to equal the nine-path manifest exactly; verify every per-file checksum, both patch checksums, ordered manifest checksum, supplementary fingerprints, OCI index/amd64 children, and `git diff --check`. Abort on drift

Build only with `docker build --platform linux/amd64 --pull=false`. Retain all TASK-014/TASK-006 package, glibc, Python 3.13.15, cpython-313 ABI/SOABI, system-venv, uvloop, Prisma, Rust/Maturin, native import, package/SPDX, normal-entrypoint, and immutable image identity gates

Run the normal entrypoint in a disposable isolated network/container with secret-free settings and `PROXY_BASE_URL=https://candidate.invalid`. Execute all six discovery aliases, exact aggregate/scoped/toolset no-token and invalid-token challenges, selection-header invariance, repeated reconnect with zero discovery 404s, readiness, `/mcp`, MCP REST, management tool-list, upstream preservation, and explicit toolset challenge-before-DB behavior. Exercise authorized initialize/tool behavior only where possible without production credentials/database; mark only genuinely environment-bound sub-gates BLOCKED rather than weakening them

Record production container/image/readiness invariants before and after. Do not mount production credentials or databases, do not stop/restart/replace production, and remove disposable container/network/worktree after evidence capture. Signature/attestation, aggregate SBOM, comparative scanners, Critical/High disposition, arm64, promotion, publication, deployment, and production mutation remain unauthorized pending separate evidence and review

### Documentation Impact

The architecture contract matches reviewed runtime behavior. No product documentation update is required

### Signed Reopen 7 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Reopen 7 closes all anonymous/toolset and context findings. A new isolated amd64 candidate is authorized only from the exact nine-path manifest, checksums, pinned OCI provenance, and build/smoke constraints above. The retained prior image is obsolete; promotion and deployment remain unauthorized
