# TASK-2026-08-26-019 Evidence Summary

## Final Result

PASS. Fedora and NAS now persistently expose neither normal GPT-5.3 Codex nor Spark routes or fallbacks. NAS also no longer exposes `defend/gpt-5.5` or any fallback dependency on it. Fresh OpenCode plugin 0.2.2 and Codex 0.149.1 discovery omit both GPT-5.3 families

## Acceptance Criteria Coverage

- **T5-AC-1: PASS.** Fresh protected backups, SHA-256 checks, restore listings, exact recreation payloads, identities, dependencies, defaults, and access inventories covered all expanded targets
- **T5-AC-2: PASS.** Fedora removed both exact normal GPT-5.3 deployments and reciprocal fallbacks through authenticated host-local APIs. No Spark route was present
- **T5-AC-3: PASS.** Fedora readiness, restart persistence, raw DB, model/group/router, access, and unavailable-without-redirect gates passed
- **T5-AC-4: PASS.** Reopen 2 removed all exact NAS target dependencies and seven deployments through authenticated host-local APIs
- **T5-AC-5: PASS.** Readiness, DB connectivity, restart persistence, raw/projection absence, exact unrelated identity/access equality, scoped-error checks, and unavailable behavior passed
- **T5-AC-6: PASS.** Fresh OpenCode with plugin 0.2.2 exposed zero GPT-5.3 aliases; fresh Codex 0.149.1 returned eight rows and zero GPT-5.3 aliases
- **T5-AC-7: PASS.** All tested retired aliases returned ordinary HTTP 400 unavailable behavior without a deployment identity header. Fresh rollback assets can recreate every exact removed row and fallback

## Protected Rollback Assets

- NAS host-local directory: `/home/staticduo/docker/litellm/backups/TASK-2026-08-26-019/`, mode `0700`
- Fedora host-local directory: `/home/staticduo/docker/litellm/backups/TASK-2026-08-26-019/`, mode `0700`
- Both directories contain mode `0600` custom-format dumps, SHA-256 files, successful `pg_restore --list` output, authenticated API preflight snapshots, exact raw target rows, and decrypted `/model/new` recreation payloads protected on-host
- No credential-bearing payload, authorization material, raw configuration, prompt, or model output was copied into repository evidence

## Historical Intermediate Stop, Superseded

Before any initial NAS write, Spark's mandatory preservation gate returned HTTP 400 twice and correctly stopped that execution attempt. Investigation then established the supported-surface limitation, the user approved retiring Spark everywhere, and the task reopened under the expanded retirement criteria. This stop reason is historical and does not qualify the final PASS above

## Documentation Impact

The approved SCR and plan now state the implemented final behavior: both GPT-5.3 families are retired everywhere, NAS defend is retired, and no retired alias redirects. This summary records the final PASS; the intermediate stop remains only as decision history

## Validation

- `git diff --check`: PASS
- Repository evidence secret scan: PASS for known credential and authorization patterns
- `staticeng_validate`: FAIL on pre-existing repository-wide missing CodeMaps outside this task's runtime-only scope
- `staticeng_repair` dry-run: no deterministic CodeMap repair available; unresolved directories require separate module-boundary decisions, so no unrelated repair was applied
