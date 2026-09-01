# TASK-2026-08-26-021A Evidence Summary

## Result

Approved, committed, pushed, and published `@staticeng/opencode-litellm@0.2.1`. The trusted GitHub workflow repeated the known npm OIDC HTTP 404 after all workflow gates and provenance signing; the explicitly authorized protected `.npmjs` fallback then published the exact independently reproduced tarball. An isolated official OpenCode 1.18.23 process resolved the unversioned package to exactly one 0.2.1 instance and initialized 36 live NAS metadata models without inference or shared-state mutation.

## Acceptance Criteria Coverage

- **AC-1: PASS.** Independently reviewed the exact five-file diff and Task 021 evidence. Live endpoints remain direct `{data: array}` envelopes (33 deployment rows and 42 group rows). Existing shared cache inventory independently confirms multiple package identities, including stale `@latest` 0.1.0; current 0.2.x source normalizes before filtering and has no runtime source drift.
- **AC-2: PASS.** Clean `npm ci`, build, 63/63 tests, production audit, tracked-dist check, 19-file pack inventory, and two byte-identical packs passed. Both SHA-256 values equal the approved `ce9a42bfab697f1124376d6665619e8b11b4aa009ee9dc03de9fe702fc7b8fd6`.
- **AC-3: PASS.** Commit `1d5e8e632fcfa1db03ce88a79b3ae924cadf6855` contains only `package.json`, `package-lock.json`, `test/codemap.yml`, `test/litellm.test.mjs`, and `test/model-groups.test.mjs`; push to `origin/main` succeeded. Pre-existing unrelated worktree artifacts were excluded.
- **AC-4: PASS.** GitHub release `v0.2.1` exists. Trusted publish run `33039382103` repeated the known npm PUT 404 after identity/build/test/dist/pack/provenance gates. Authorized fallback published the exact verified tarball. npm `latest` is 0.2.1; registry integrity is `sha512-KJ4RFk4gVPjYZ6rCihkMcHGl1dxOjKKYTrZhNj8oS8sO8LMEaLgVSI8ufQc9T66aOWXSIxO+QIb6Y0xfZRZD2w==`; downloaded tarball SHA-256 matches the approved candidate byte-for-byte.
- **AC-5: PASS.** Isolated official OpenCode 1.18.23 with the exact unversioned package reference installed one package instance at 0.2.1, logged one successful metadata initialization, exposed 36 models including Sol, DeepSeek V4, Qwen3.8, and Spark, excluded retired normal GPT-5.3 Codex, emitted no `models.filter` failure, and made no inference request.
- **AC-6: PASS.** Complete redacted evidence and exact Task 017 cache inventory/removal guidance are recorded below. No shared configuration or shared cache was modified.

## Cache Inventory and Task 017 Guidance

Current shared host inventory under `/home/staticduo/.cache/opencode/packages/`:

- `@staticeng/opencode-litellm@latest` resolves stale 0.1.0 and is the duplicate failure source.
- `@staticeng/opencode-litellm` resolves 0.2.0 and is stale after this release.
- Explicit historical caches `@staticeng/opencode-litellm@0.1.7` and `@staticeng/opencode-litellm@0.1.8` are not selected by the unversioned reference but must not be confused with its active cache.

For Task 017, stop every OpenCode process using the shared cache, inventory package versions first, then remove or quarantine only these unversioned selector directories:

- `/home/staticduo/.cache/opencode/packages/@staticeng/opencode-litellm`
- `/home/staticduo/.cache/opencode/packages/@staticeng/opencode-litellm@latest`

Do not remove explicit historical version directories unless separately approved. Restart one process with the unchanged unversioned config, verify exactly one package directory is selected and its nested package version is 0.2.1, then require one `loaded LiteLLM provider metadata` success and zero stale-plugin/load/filter errors before proceeding host-by-host. Repeat the inventory and scoped invalidation independently on every connected Task 017 host; do not assume Syncthing manages caches.

## Documentation Impact

No product or architecture documentation change is required because runtime behavior and `dist/` are unchanged. `test/codemap.yml` records the expanded verification coverage.

## Validation Note

`staticeng_validate` remains blocked by the governing LiteLLM repository's pre-existing broad CodeMap backlog. Required repair dry-run found no safe deterministic CodeMap fix for that backlog. This release introduced no governing-repository source or CodeMap change.

## Open Risks

- npm trusted publishing remains broken with the known OIDC HTTP 404 and should be repaired separately; 0.2.1 was published through the authorized protected fallback without credential disclosure.
- Shared production hosts still contain stale duplicate caches until Task 017 performs scoped host-by-host invalidation.

## Recommended Next Step

PMA should reopen Task 017 and execute the documented cache invalidation and shared-config migration gates without changing the unversioned package reference.
