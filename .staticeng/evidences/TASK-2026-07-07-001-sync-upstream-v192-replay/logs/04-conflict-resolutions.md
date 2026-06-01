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
