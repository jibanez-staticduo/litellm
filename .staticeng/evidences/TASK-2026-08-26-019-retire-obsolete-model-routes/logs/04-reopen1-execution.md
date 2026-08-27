# Reopen 1 Execution

## Fresh Backups

| Host | Dump bytes | SHA-256 | Restore listing |
| --- | ---: | --- | ---: |
| Fedora | 75,017,755 | `b490df967c9e49224372e021ea79c02848496f6c4af8126966215978c376f7e4` | 417 entries |
| NAS | 1,866,888,629 | recorded and verified in protected host-local `.sha256` file | 415 entries |

Both custom-format dumps passed `sha256sum -c` and `pg_restore --list`. Mode `0600` dumps, listings, authenticated snapshots, and exact recreation payloads remain under mode `0700` host-local Reopen 1 directories

## Fresh Targets

Fedora had two normal GPT-5.3 deployments and two reciprocal general fallbacks. It had no Spark deployment, group, fallback, default, alias, or routing group

NAS had three normal deployments, three Spark deployments, `defend/gpt-5.5`, one normal public fallback, one Spark public fallback, and six exact defend-related fallback entries. No target was a default, model-group alias, or routing group

## Fedora

- Removed two reciprocal fallbacks through authenticated host-local `/config/update`
- Deleted IDs `b175303a-eb59-43e4-ad65-22c42a98c649` and `51d9260e-ac4d-4294-ab95-930afdb5a012` through authenticated host-local `/model/delete`
- Restarted the existing container and reached healthy readiness with DB connected
- Raw DB target count: zero
- `/model/info`, `/model_group/info`, `/router/settings`, and `/v1/models` target references: zero
- Non-target deployment and access projection matched the fresh preflight projection exactly
- Five normal/Spark alias requests returned ordinary HTTP 400 unavailable behavior with no deployment identity header

## NAS

- Removed all normal, Spark, and defend target references from the 16-entry fallback list, preserving 12 non-empty unrelated mappings
- Deleted seven exact target IDs through authenticated host-local `/model/delete`
- Restarted and passed readiness, raw DB absence, all model/group/router absence, exact non-target identity preservation, and unavailable-without-redirect checks
- Fresh client discovery then failed: OpenCode exposed one Spark alias on both hosts and Codex 0.149.1 exposed Spark in `model/list`
- Restored all seven exact deployments with protected `/model/new` payloads, including original UUIDs, then restored all 16 original fallback entries through authenticated `/config/update`
- Restarted and verified readiness, all seven exact DB IDs, and target projections

No direct DB write was used. No prompt or model output was retained
