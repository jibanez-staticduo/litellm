# Conflict Resolutions

## 7909b12b89 fix(auth): coerce cached key dicts in common checks

- File: `tests/test_litellm/proxy/auth/test_user_api_key_auth.py`
- Conflict: upstream added budget reservation disable/control tests in the same section where the local commit added cached-key-dict common-check regression coverage.
- Resolution: kept the upstream budget reservation tests and added `test_common_checks_accepts_cached_key_dict` immediately after them, preserving both upstream coverage and the local cached key dict regression test.
- Secrets: none logged.

## f11607cbf3 fix(auth): handle cached user dict limits

- File: `litellm/proxy/auth/user_api_key_auth.py`
- Conflict: upstream kept `_route_requires_auth_despite_public` adjacent to the local helper insertion point for cached user dict value access.
- Resolution: added `_get_user_obj_value` before `_route_requires_auth_despite_public` and preserved the upstream single-line route auth helper signature.
- File: `tests/test_litellm/proxy/auth/test_user_api_key_auth.py`
- Conflict: no content conflict; the commit added cached user dict limit regression coverage cleanly.
- Resolution: kept `test_return_user_api_key_auth_obj_cached_user_dict_limits` alongside the existing object-attribute test.
- Secrets: none logged.

## 08a3aac163 fix(auth): use cached user dict accessor

- File: `litellm/proxy/auth/auth_checks.py`
- Conflict: upstream had concurrent budget-check refactoring and alert-email formatting while the local commit replaced direct user object attributes with a dict-safe accessor.
- Resolution: preserved upstream concurrent budget-check structure, `get_current_spend(max_budget=...)`, and alert config flow while using `_get_user_object_value` for `max_budget`, `user_id`, `spend`, `user_role`, and owner email.
- File: `litellm/proxy/auth/user_api_key_auth.py`
- Conflict: previous local `_get_user_obj_value` helper overlapped with this commit moving the shared accessor into `auth_checks.py`, and JWT user role/limit fields conflicted with direct attribute reads.
- Resolution: removed the local helper, kept importing `_get_user_object_value`, and used it for JWT user role, TPM, and RPM fields.
- File: `litellm/proxy/auth/route_checks.py`
- Conflict: no content conflict; commit updated route checks to read user dicts and objects through `_get_user_object_value`.
- Resolution: kept the staged route check accessor changes.
- File: `tests/test_litellm/proxy/auth/test_user_api_key_auth.py`
- Conflict: no content conflict; commit added shared accessor regression coverage.
- Resolution: kept `_get_user_object_value` import and `test_get_user_object_value_reads_cached_user_dict_and_object`.
- Secrets: none logged.

## f424f1bda1 fix: TASK-2026-06-08-002 repair MCP and spend logs

- File: `litellm/proxy/spend_tracking/spend_management_endpoints.py`
- Conflict: upstream had moved spend log access to `SpendLogsRepository`, while the local commit rejected unbounded legacy `/spend/logs` queries and routed filtered legacy list requests through a lightweight column query.
- Resolution: kept upstream `SpendLogsRepository` for `request_id` exact log lookups and summary grouping, preserved the local unbounded-query rejection, and preserved `_get_legacy_spend_logs_without_heavy_columns` for non-`request_id` filtered legacy responses.
- File: `litellm/proxy/_experimental/mcp_server/ui_session_utils.py`
- Conflict: no content conflict; local commit added dict-safe UI session team resolution.
- Resolution: kept dict/object team extraction for cached UI session users.
- File: `tests/test_litellm/proxy/spend_tracking/test_spend_management_endpoints.py`
- Conflict: no content conflict; local commit added legacy spend log rejection coverage and updated mock query path.
- Resolution: kept the test updates.
- Secrets: none logged.

## 067be69f8f fix: TASK-2026-06-10-001 clean stale MCP delete refs

- File: `.gitignore`
- Conflict: upstream added coverage/dashboard output ignores while the local commit added StaticEng private-state ignore rules.
- Resolution: kept both upstream ignore rules and StaticEng private-state ignore rules.
- File: `litellm/proxy/_experimental/mcp_server/db.py`
- Conflict: upstream retained `TYPE_CHECKING` imports and existing delete cleanup while the local commit added tuple typing plus stale object-permission cleanup helpers before MCP server delete.
- Resolution: kept `TYPE_CHECKING` and `Tuple`, added `_get_mcp_tool_permissions_without_server` and `cleanup_mcp_server_references`, and preserved upstream `delete_mcp_server` per-user credential/env best-effort cleanup.
- File: `litellm/proxy/management_helpers/object_permission_utils.py`
- Conflict: upstream preserved unresolved server IDs in team allowed MCP resolution, while the local commit intentionally drops stale/deleted MCP server IDs.
- Resolution: used the local stale-reference cleanup behavior by returning only `_flatten_resolved_mcp_server_ids(resolved_servers)`.
- File: `tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
- Conflict: import list conflicted between upstream `_rewrite_object_permission_mcp_servers` coverage and local `_resolve_mcp_server_identifiers_to_ids` stale-id coverage.
- Resolution: kept both imports and both test groups.
- Secrets: none logged.
