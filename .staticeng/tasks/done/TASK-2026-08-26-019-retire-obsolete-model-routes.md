---
id: TASK-2026-08-26-019-retire-obsolete-model-routes
complexity: complex
track: implementation
slice: core
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 2
---

# Task: TASK-2026-08-26-019 - Retire Obsolete Model Routes

## Objective
Retire normal GPT-5.3 Codex and Spark routes Fedora-first and then NAS, plus NAS `defend/gpt-5.5`, while preserving unrelated routes.

## Acceptance Criteria
- [x] T5-AC-1: Re-enumerate exact normal/Spark/defend IDs, dependencies, access, defaults, and fallbacks; create protected DB backups, restore listings, and recreation payloads on both hosts.
- [x] T5-AC-2: Delete exact Fedora normal GPT-5.3 and any Spark deployments through Fedora host-local admin API only; no NAS write yet.
- [x] T5-AC-3: Fedora passes readiness, DB/model/group/fallback/router/access/log/persistence gates; both retired families unavailable without redirect.
- [x] T5-AC-4: Delete exact NAS normal GPT-5.3 and Spark deployments/fallbacks and `defend/gpt-5.5` plus exact dependencies through NAS host-local APIs only; no other route change.
- [x] T5-AC-5: NAS passes readiness, persistence, absence, access, scoped-log, and no-redirect gates.
- [x] T5-AC-6: Fresh OpenCode/Codex discovery omits both retired GPT-5.3 families.
- [x] T5-AC-7: No retired alias silently redirects to Spark or another model; complete rollback assets/evidence exist.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-019-retire-obsolete-model-routes/` with `SUMMARY.md` and redacted logs.

## Stop Conditions
Stop before writes if any target/dependency/recreation payload cannot be proven. On Fedora failure, rollback Fedora and leave NAS untouched. Use supported APIs, never direct DB writes.

## Reopen History

### Reopen 1 - 2026-08-27
- Initial execution stopped before writes because NAS Spark returned HTTP 400.
- Investigation confirmed Spark exact identifier but Pro-only/no public API restrictions, incorrect route/catalog metadata, and no successful entitlement proof.
- User approved retiring Spark everywhere rather than repairing it.
- Re-enumerate and retire both normal GPT-5.3 and Spark exact routes/dependencies/fallbacks, plus NAS defend/gpt-5.5; replace Spark-preservation gates with absence/no-redirect/rollback gates.

### Reopen 2 - 2026-08-27
- Client retirement completed: published plugin `0.2.2` and Codex catalog both omit normal GPT-5.3 and Spark.
- Fedora retirement remains applied and previously passed all gates.
- Re-enumerate current NAS state and repeat only NAS retirement of normal GPT-5.3, Spark, and `defend/gpt-5.5`, then run final client-discovery absence gates.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Execution stopped before writes because NAS Spark did not pass the mandatory pre-mutation functional gate; two bounded status-only requests returned HTTP 400
- Fresh Fedora inventory found two normal GPT-5.3 deployments and two reciprocal general fallbacks; Fedora has no Spark deployment
- Fresh NAS inventory found three normal GPT-5.3 deployments, their public fallback, `defend/gpt-5.5`, all defend inbound/outbound fallback dependencies, and three retained Spark identities
- Protected host-local custom-format database backups, checksums, restore listings, raw rows, authenticated snapshots, and exact `/model/new` recreation payloads were created on both hosts
- No source, configuration, client catalog, fallback, deployment, or database row was changed; no rollback was needed and NAS remained untouched
- Evidence: `.staticeng/evidences/TASK-2026-08-26-019-retire-obsolete-model-routes/`

## Tech Lead: Reopen 1 Post Implementation Expectations

- Fresh Reopen 1 backups, checksums, restore listings, and exact protected recreation payloads covered both GPT-5.3 families and NAS `defend/gpt-5.5`
- Fedora retired two exact normal deployments and both reciprocal fallbacks through host-local APIs; Fedora had no Spark deployment. Restart persistence, raw DB absence, model/group/router absence, access equality, readiness, and unavailable-without-redirect gates passed
- NAS removed seven exact deployments and all approved target fallback references through host-local APIs, then passed registry and no-redirect gates
- Fresh client discovery still exposed Spark in both OpenCode and Codex because client catalogs/configuration remain stale and this task explicitly forbids editing them
- The failed T5-AC-6 gate triggered immediate NAS rollback through exact `/model/new` payloads and restored router settings. NAS readiness, seven exact IDs, and 16 original fallbacks persisted after restart; Fedora remains successfully retired
- No direct DB write, source edit, client configuration edit, prompt retention, or model-output retention occurred

## Tech Lead: Reopen 2 Post Implementation Expectations

- Fresh NAS inventory proved Reopen 1 rollback restored the same seven target UUIDs, 16 fallback entries, two-team access memberships, and empty default/alias/routing-group dependencies
- Created a fresh protected custom-format PostgreSQL backup, checksum, restore listing, authenticated snapshot, and exact credential-complete `/model/new` recreation payloads
- Removed every exact normal GPT-5.3, Spark, and defend fallback reference before deleting the seven target deployments through authenticated NAS host-local APIs
- Restart persistence passed: readiness and DB connectivity remained healthy; raw DB, model, group, router, and discovery projections contain zero target references
- All seven retired aliases returned ordinary HTTP 400 unavailable behavior without a deployment identity header; unrelated deployment identities and access memberships are exactly unchanged
- Fresh OpenCode loaded cached plugin `0.2.2` and exposed no GPT-5.3 alias; fresh Codex 0.149.1 returned eight rows with neither retired family
- Fedora remains healthy with zero GPT-5.3 route or fallback references, completing dual-host retirement
- No rollback was required. No source/config/catalog edit, direct DB write, prompt retention, or model-output retention occurred
