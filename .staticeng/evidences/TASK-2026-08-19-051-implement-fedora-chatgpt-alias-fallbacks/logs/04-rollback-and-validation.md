# Rollback And Validation

## Health And Equality

- Readiness: HTTP 200
- Liveliness: HTTP 200
- Container health: healthy
- Restart count: 0
- Reload/restart required: no; database and fallback API changes appeared in live readback
- Persistent/live equality: six exact matching account2 rules
- Final public association count: six account1 absent-profile records
- Final qualified counts: six account1 and six account2 records, unchanged

## Rollback

- Rollback required: no
- Transaction mismatch behavior: exception and rollback inside one transaction
- Exact five-value restore SQL: protected, five lines, mode `0600`, integrity hash recorded in preflight evidence
- Exact six-rule fallback before-state: protected mode-`0600` snapshot, restored only through supported fallback APIs if needed
- Restore-readiness: exact row identities, aliases, and before-values are embedded in protected SQL predicates; expected statement count is five

## Secret Safety

PASS. Repository evidence contains no authorization material, credentials, raw profile values, identities, account IDs, raw deployment IDs, prompts, responses, or unrelated logs. Exact encrypted database values remain only in owner-protected Fedora rollback material

## StaticEng Validation

`staticeng_validate` was rerun and remains failed on pre-existing repository-wide broken `.staticeng/codemap.yml` links and missing CodeMaps. No broad repair was applied because it would modify unrelated metadata and concurrent work outside this operational task
