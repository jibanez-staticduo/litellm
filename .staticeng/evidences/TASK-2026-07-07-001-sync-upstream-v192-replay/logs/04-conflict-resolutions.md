# Conflict Resolutions

## 7909b12b89 fix(auth): coerce cached key dicts in common checks

- File: `tests/test_litellm/proxy/auth/test_user_api_key_auth.py`
- Conflict: upstream added budget reservation disable/control tests in the same section where the local commit added cached-key-dict common-check regression coverage.
- Resolution: kept the upstream budget reservation tests and added `test_common_checks_accepts_cached_key_dict` immediately after them, preserving both upstream coverage and the local cached key dict regression test.
- Secrets: none logged.
