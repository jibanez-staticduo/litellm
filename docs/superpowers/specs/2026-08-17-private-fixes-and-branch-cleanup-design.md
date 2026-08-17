# Private Fixes And Branch Cleanup Design

## Goal

Recover the remaining valuable private behavior into `main`, verify and publish it, then remove every obsolete branch from the fork while retaining `upstream/main` as the only upstream tracking reference.

## Scope

The implementation contains three independent code changes:

1. Keep the direct `/lazymcp` routes in the gateway component
2. Keep the fail-closed client IP sentinel limited to LazyMCP and preserve the established standard MCP behavior when no verified IP exists
3. Process key and team `budget_limits` rows in bounded raw SQL batches without returning to the incompatible Prisma JSON filter

The cleanup happens only after all three changes are committed, verified, pushed to `origin/main`, and fetched back successfully.

## Gateway LazyMCP Routing

`gateway/routes/allowlist.py` will include `/lazymcp` as a gateway path prefix. The component allowlist test will exercise the real gateway predicate for `/lazymcp` and `/lazymcp/{server}` so future route-table changes cannot silently remove the direct LazyMCP data-plane surface. Existing `/toolset/{name}/lazymcp` behavior remains unchanged.

## Standard MCP Client IP Behavior

The Responses MCP bridge will pass the fail-closed sentinel through the LazyMCP path, but convert that sentinel to `None` before standard MCP discovery. A verified client IP remains unchanged. Regression tests will cover both missing and verified IP cases through the real `_get_mcp_tools_from_manager` routing decision.

## Budget Window Pagination

`ResetBudgetJob.reset_budget_windows` will retain raw SQL and `budget_limits IS NOT NULL`. Keys and teams will be read using deterministic keyset pagination with `ORDER BY`, a strict `LIMIT`, and the previous page's final identifier as the next cursor. The implementation will not use the old Prisma `Json?` filter or OFFSET pagination.

Tests will prove that:

- every query is bounded
- a full batch triggers another query with the correct cursor
- a short batch terminates iteration
- key and team processing remain independent when one query path fails
- existing reset and counter behavior remains unchanged

## Git And Branch Cleanup

The current isolated branch `merge_upstream_main_20260816` will be used only until its verified HEAD is pushed to `origin/main`. After remote verification:

- every `origin` branch except `main` will be deleted, including private backups and upstream-derived copies
- the linked integration worktree will be removed
- every local branch except the active dirty `main` checkout will be deleted
- the `upstream` fetch refspec will be narrowed to `refs/heads/main:refs/remotes/upstream/main`
- existing local `upstream/*` tracking refs other than `upstream/main` will be deleted
- no deletion will be attempted against the actual BerriAI upstream repository

The dirty checkout at `/home/staticduo/git/litellm` will not be reset, restored, stashed, rebased, or switched. Its branch pointer will remain untouched if moving it would alter the interpretation of the user's uncommitted files.

## Verification

Each behavior will follow a red-green test cycle. Before each commit, the relevant focused tests and `make pre-commit` will pass. Before cleanup, `origin/main` must equal the verified implementation HEAD and contain both the previous fork main and `upstream/main` as ancestors. After cleanup, remote and local branch inventories must show only the intended `main` references, and the primary checkout's original uncommitted files must still be present.
