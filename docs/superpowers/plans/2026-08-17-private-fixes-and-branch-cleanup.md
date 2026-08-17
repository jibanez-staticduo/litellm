# Private Fixes And Branch Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover three valuable private behaviors into `main`, publish the verified result, and remove every obsolete fork branch while retaining only `upstream/main` for future synchronization.

**Architecture:** Each behavior is implemented and committed independently through a red-green test cycle. Branch deletion is a final operational task that runs only after `origin/main` is fetched back at the exact verified implementation SHA.

**Tech Stack:** Python 3.11+, pytest, FastAPI/Starlette route tables, Prisma raw SQL, Git and GitHub SSH remote operations

## Global Constraints

- Preserve all uncommitted files in `/home/staticduo/git/litellm`
- Do not reset, restore, stash, rebase, switch, or update the dirty local `main` pointer
- Do not delete or mutate branches in the actual BerriAI upstream repository
- Use raw SQL keyset pagination for `budget_limits`; do not restore the old Prisma JSON filter
- Run focused tests and `make pre-commit` immediately before each code commit
- Push without force and verify the fetched `origin/main` SHA before deleting branches

---

### Task 1: Expose Direct LazyMCP Routes On Gateway

**Files:**
- Modify: `gateway/routes/allowlist.py`
- Test: `tests/test_litellm/proxy/test_component_allowlists.py`

**Interfaces:**
- Consumes: `gateway.main._is_gateway_route(route) -> bool`
- Produces: direct `/lazymcp` and `/lazymcp/{mcp_server_name}` routes retained by the gateway component

- [ ] **Step 1: Write the failing route-retention test**

Add a parametrized test that creates `fastapi.routing.APIRoute` instances for `/lazymcp` and `/lazymcp/{mcp_server_name}` and asserts `_is_gateway_route(route)` is true.

- [ ] **Step 2: Run the test and verify RED**

Run: `uv run --no-sync pytest -q tests/test_litellm/proxy/test_component_allowlists.py -k lazymcp`

Expected: both direct LazyMCP cases fail because `GATEWAY_PATH_PREFIXES` does not contain `/lazymcp`.

- [ ] **Step 3: Implement the minimal allowlist change**

Add the string `"/lazymcp"` to `GATEWAY_PATH_PREFIXES` next to the dynamic provider and toolset data-plane routes.

- [ ] **Step 4: Verify GREEN and the component coverage suite**

Run: `uv run --no-sync pytest -q tests/test_litellm/proxy/test_component_allowlists.py`

Expected: all component allowlist tests pass.

- [ ] **Step 5: Gate and commit**

Run `git add gateway/routes/allowlist.py tests/test_litellm/proxy/test_component_allowlists.py`, then `make pre-commit`, then commit as `fix(gateway): expose direct LazyMCP routes`.

### Task 2: Preserve Standard MCP Missing-IP Behavior

**Files:**
- Modify: `litellm/responses/mcp/litellm_proxy_mcp_handler.py`
- Test: `tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py`

**Interfaces:**
- Consumes: `ResponsesAPIRequestUtils.get_verified_mcp_client_ip` fail-closed sentinel
- Produces: sentinel retained for LazyMCP, converted to `None` only for standard MCP discovery, verified IPs unchanged

- [ ] **Step 1: Write two routing regression tests**

Add tests that call the real `_get_mcp_tools_from_manager` standard MCP branch while replacing the server-listing boundary with an `AsyncMock`. Assert the boundary receives `None` for `__invalid_mcp_client_ip__` and receives `10.0.0.7` unchanged for a verified address.

- [ ] **Step 2: Run the tests and verify RED**

Run: `uv run --no-sync pytest -q tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py -k 'standard_mcp_preserves_missing_client_ip_behavior or standard_mcp_keeps_verified_client_ip'`

Expected: the missing-IP test fails because the standard branch currently forwards `__invalid_mcp_client_ip__`.

- [ ] **Step 3: Implement the minimal branch-specific normalization**

Before `_get_standard_mcp_tools`, bind `standard_client_ip` to `None` only when `client_ip == "__invalid_mcp_client_ip__"`; otherwise retain `client_ip`. Pass `standard_client_ip` to the standard MCP helper. Do not modify the LazyMCP branch.

- [ ] **Step 4: Verify GREEN and the focused MCP module**

Run: `uv run --no-sync pytest -q tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py`

Expected: the complete handler test module passes.

- [ ] **Step 5: Gate and commit**

Run `git add litellm/responses/mcp/litellm_proxy_mcp_handler.py tests/test_litellm/responses/mcp/test_litellm_proxy_mcp_handler.py`, then `make pre-commit`, then commit as `fix(mcp): preserve standard Responses IP behavior`.

### Task 3: Paginate Budget Window Rows With Raw SQL

**Files:**
- Modify: `litellm/proxy/common_utils/reset_budget_job.py`
- Test: `tests/test_litellm/proxy/common_utils/test_reset_budget_job.py`

**Interfaces:**
- Consumes: `RESET_BUDGET_JOB_BATCH_SIZE`, `RESET_BUDGET_JOB_MAX_CHUNKS_PER_RUN`, Prisma `query_raw(sql, *params)`
- Produces: bounded key and team scans using primary-key cursors and deterministic ordering

- [ ] **Step 1: Write failing key and team pagination tests**

Extend the reset-budget test helper so `query_raw` records SQL and parameters and can return multiple batches. Add tests asserting first-page SQL includes `ORDER BY token ASC LIMIT $1`, continuation SQL includes `token > $1` and `LIMIT $2`, and the equivalent `team_id` clauses are used for teams. Use a full first batch and a short second batch to prove continuation and termination.

- [ ] **Step 2: Run the tests and verify RED**

Run: `uv run --no-sync pytest -q tests/test_litellm/proxy/common_utils/test_reset_budget_job.py -k 'budget_windows and paginat'`

Expected: tests fail because each table currently executes one unbounded raw query.

- [ ] **Step 3: Implement bounded raw SQL pages**

Add key and team page readers that use fixed SQL strings. The first page uses `WHERE budget_limits IS NOT NULL ORDER BY <id> ASC LIMIT $1`; later pages add `AND <id> > $1 ORDER BY <id> ASC LIMIT $2`. Reuse `RESET_BUDGET_JOB_BATCH_SIZE` and cap traversal with `RESET_BUDGET_JOB_MAX_CHUNKS_PER_RUN`. Advance each cursor from the final identifier in the returned batch. Keep key and team exception boundaries separate.

- [ ] **Step 4: Verify GREEN and existing reset semantics**

Run: `uv run --no-sync pytest -q tests/test_litellm/proxy/common_utils/test_reset_budget_job.py`

Expected: pagination regressions and all existing reset-budget tests pass.

- [ ] **Step 5: Gate and commit**

Run `git add litellm/proxy/common_utils/reset_budget_job.py tests/test_litellm/proxy/common_utils/test_reset_budget_job.py`, then `make pre-commit`, then commit as `perf(proxy): paginate budget window resets`.

### Task 4: Publish And Clean Branches

**Files:**
- Verify: Git refs and remote configuration only

**Interfaces:**
- Consumes: verified implementation HEAD and current `origin/main`
- Produces: `origin/main` as the only fork branch and `upstream/main` as the only locally tracked upstream branch

- [ ] **Step 1: Run final verification**

Run all three focused suites together, then `make pre-commit`. Verify `git status --short` is empty and both the previous `origin/main` and `upstream/main` are ancestors of HEAD.

- [ ] **Step 2: Push and verify the remote**

Run `git push origin HEAD:main`, fetch `origin main`, and require `git rev-parse HEAD` to equal `git rev-parse origin/main`.

- [ ] **Step 3: Resolve exact deletion targets**

Capture every `refs/remotes/origin/*` branch except `origin/main`. Confirm the set excludes `main`, then delete those branches from `origin` in bounded batches without force-pushing any retained ref.

- [ ] **Step 4: Remove the integration worktree and local obsolete branches**

Remove `/tmp/litellm-upstream-main-merge-20260816` from outside the worktree. Delete every local branch except the active dirty `main`, including `merge_upstream_main_20260816`.

- [ ] **Step 5: Narrow upstream tracking**

Set `remote.upstream.fetch` to `+refs/heads/main:refs/remotes/upstream/main`. Delete local `refs/remotes/upstream/*` tracking refs except `upstream/main`, then fetch `upstream main` once.

- [ ] **Step 6: Verify final repository state**

Require the remote fork branch list to contain only `main`, the local branch list to contain only `main`, and the upstream tracking list to contain only `upstream/main`. Re-read the dirty checkout status and confirm its original uncommitted paths remain present.
