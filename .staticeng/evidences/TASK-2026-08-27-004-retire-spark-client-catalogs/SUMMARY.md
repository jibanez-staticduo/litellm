# TASK-2026-08-27-004 Evidence Summary

## Result

PASS. Client catalogs now retire both exact GPT-5.3 Codex families without route writes, inference, or binary patches. `@staticeng/opencode-litellm@0.2.2` is npm `latest`; fresh OpenCode clients omit both families, and the NAS Codex custom catalog retains eight non-GPT-5.3 rows with active DeepSeek `high` unchanged

## Acceptance Criteria Coverage

- **AC-1: PASS.** The immutable retired set contains the four exact normal and four exact Spark aliases. Spark is no longer active. All eight remaining families, ordered modes, defaults, unknown/near-match behavior, and explicit model/provider override precedence remain covered by 63 passing tests
- **AC-2: PASS.** Version, tests, README, architecture documentation, source/test CodeMaps, and tracked `dist/model-contracts.js` were updated. Clean install/build/test/tracked-dist/pack passed. Fresh official OpenCode `1.18.23` discovery on NAS, Fedora, DG2, and Pi5 returned 33 models, retained GPT-5.4/5.5/5.6, DeepSeek, Qwen, and unrelated rows, and omitted both GPT-5.3 families
- **AC-3: PASS.** Commits `1617d86` and `b14e16c` were pushed non-force to `origin/main`, tag/release `v0.2.2` points at `b14e16c`, and trusted run `33049626751` passed identity, install, build, 63 tests, tracked dist, pack, and provenance signing before repeating the known npm PUT 404. The previously authorized protected `.npmjs` fallback published the exact reviewed tarball. npm `latest` is `0.2.2`
- **AC-4: PASS.** Only the exact unversioned `@staticeng/opencode-litellm` and `@latest` cache identities were removed. NAS, Fedora, DG2, and Pi5 rebuilt one `@latest` `0.2.2` tree through fresh official clients. DG1 lacks an official OpenCode runtime and now has no stale exact-identity tree. Unrelated cache paths were preserved
- **AC-5: PASS.** Fresh owner-only backups cover NAS Codex config, custom catalog, and generated cache. One exact Spark row was atomically removed, reducing nine rows to eight. `config.toml` remains byte-identical with active DeepSeek `high`, the Responses provider, custom catalog path, `[execution]`, and unrelated settings unchanged. Fresh isolated Codex `0.149.1` `model/list` returned eight retained rows and neither GPT-5.3 family. Production generated cache was not edited
- **AC-6: PASS.** Syncthing configuration was not changed. NAS, Win, Fedora, DG1, DG2, and Pi5-Torre are currently reachable through the supported API; the shared OpenCode folder is idle with 100% completion, zero needed items/bytes/deletes, zero pull errors, and no system errors on each. Offline configured peers remain automatic convergence follow-up. Rollback assets remain protected outside synchronized paths

## Release State

- Package: `@staticeng/opencode-litellm@0.2.2`
- Git head/tag: `b14e16c1dbe9f57d037852d509501d857ca48651` / `v0.2.2`
- npm integrity: `sha512-h4pSTXgE8gTWLV4S1l0KvU3jzpKaq03nzfe1kQulZV1M+uJk/Oxi8RK1FzIqeTnHVXuTSq9ppGj1YjLIUAdxGA==`
- npm shasum: `700c1ea1e7b8b81190c002ddcafed609467d50ca`
- Tarball SHA-256: `477bbdf53a7034ef5c9f22c801a4654b3db14d18c40c64681b4764df3d08c278`
- GitHub release: `https://github.com/jibanez-staticduo/opencode-litellm/releases/tag/v0.2.2`

## Client State

- OpenCode: four fresh official `1.18.23` clients resolved one `0.2.2` package tree and exposed 33 models with both GPT-5.3 families absent
- Codex: fresh isolated `0.149.1` exposed eight custom rows with both GPT-5.3 families absent; active production selection remains DeepSeek V4 Flash at `high`
- Syncthing: shared config remains unchanged and converged across all currently reachable configured instances; no conflict or direct peer edit occurred
- Routes: untouched by this task

## Documentation Impact

The plugin README, model-contract architecture document, source/test CodeMaps, approved SCR Spark retirement decision, task closure, and this operational evidence describe the new steady state. No additional product or architecture document is required

## Validation Note

`staticeng_validate` remains blocked by the governing LiteLLM repository's pre-existing broad CodeMap backlog. The required repair dry-run found no deterministic repair for those manual module-boundary decisions. This task updated every CodeMap directly affected by its source/test changes

## Open Risks

- npm trusted publishing still fails at the known OIDC PUT step; `0.2.2` used the authorized credential fallback after exact artifact verification
- Offline Syncthing peers were not directly edited and will converge automatically when they reconnect; their plugin cache is refreshed only when they are reachable
- Pre-existing long-running OpenCode processes do not hot-reload package changes and require a normal restart to consume `0.2.2`

## Rollback

- Plugin rollback: exact prior release `0.2.1` remains available, but repinning requires explicit authorization because shared config intentionally stays unversioned
- Codex rollback: restore only the protected task backup custom catalog by atomic rename after verifying owner, mode `0600`, checksum, and unchanged config; generated cache restoration is unnecessary because it was not edited
- Cache rollback: remove only the two exact unversioned identities and allow a fresh official client to resolve the authorized target version; never remove unrelated or explicit historical package caches
