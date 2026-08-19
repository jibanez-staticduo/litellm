# NAS 1.98.0 Startup Wrapper Migration Evidence

## Summary

Created an exact mode-0600 wrapper/Compose rollback pair, removed the obsolete runtime source patches from the live NAS definitions, and passed offline candidate compatibility checks without recreating or restarting production

The wrapper and candidate are technically compatible, but the deployment decision is **REJECT** under the strict preservation gate because one live OAuth token metadata timestamp advanced during the task. No credential content was read, and all other production, dependency, inventory, routing, Fedora, and stable-tag checks remained unchanged

## Work Performed

- Backed up the exact pre-migration wrapper and Compose files with verified hashes and recorded the current 1.92.0 rollback digest
- Removed both `/app/patches` Python invocations and the inline 1.92-only site-packages health mutation
- Removed only the `/app/patches` Compose bind mount and retained both host patch files unchanged
- Preserved database fail-fast/readiness, bounded retries, guarded `source_url` repair, background repair, `litellm "$@"`, entrypoint, command, healthcheck, other mounts, and networks
- Passed shell syntax, rendered Compose, prohibited source-mutation scan, candidate image identity/binary, disposable `psql` installation, and network-isolated wrapper checks
- Did not recreate or restart production, change its image selector, alter stable, or mutate Fedora

## Acceptance Criteria Coverage

- **AC-1: PASS**. `logs/01-backup-and-migration.md` records the mode-0600 rollback pair, exact hashes, and current 1.92.0 rollback digest
- **AC-2: PASS**. `logs/01-backup-and-migration.md` records the minimal wrapper change and preserved startup behavior
- **AC-3: PASS**. `logs/02-candidate-validation.md` proves the rendered future Compose has no patch mount or runtime patch dependency while both host patch files remain unchanged
- **AC-4: PASS**. `logs/02-candidate-validation.md` records all final compatibility checks against the immutable candidate digest
- **AC-5: FAIL STRICT PRESERVATION GATE**. NAS production remained healthy and unchanged in image/container/dependency/inventory/routing terms, and Fedora remained unchanged. One live OAuth token retained the same mode and size but advanced its mtime during the task, so exact credential metadata equality cannot be claimed. See `logs/03-preservation-and-decision.md`
- **AC-6: PASS**. `logs/03-preservation-and-decision.md` records exact restoration procedures and the deployment rejection

## Documentation Impact

No product, architecture, or CodeMap update is required. This task changes only host operational files outside the repository, and this evidence records the resulting operational truth

## Open Risks

- Exact credential metadata equality was not preserved because the running service refreshed one OAuth token during the task
- The candidate wrapper still installs `postgresql-client` at startup when absent, as required by the approved architecture. The disposable candidate installation test passed
- `staticeng_validate` remains blocked by pre-existing broken links and repository-wide missing CodeMaps. The repair dry run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA and Tech Lead should keep NAS deployment blocked, review or disposition the expected live token-refresh metadata drift, then require a fresh just-in-time credential metadata baseline before authorizing the separate digest-pinned NAS deployment task
