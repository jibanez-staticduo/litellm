# TASK-2026-08-26-016 Evidence Summary

## Result

PASS after Reopen 2. The independently approved standard clean-checkout artifact for unchanged tag `v0.2.0` reproduced SHA-256 `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`, passed clean install/build/62 tests/tracked-dist/package inventory, and was published exactly once through the user-authorized protected `.npmjs` fallback. npm `latest` is `0.2.0`; the downloaded registry tarball is byte-identical with 19 files mode `0644`. Official OpenCode `1.18.23` resolved the exact unversioned package reference to installed `0.2.0` and passed representative default, explicit, override, DeepSeek, Qwen, and retirement probes.

## Reopen 2 Result

- Fresh detached worktree: unchanged `v0.2.0` commit `21f6583e9b4a112c0d2be79bbd102333de72bd89`.
- Clean verification: 62 passed, 0 failed, 0 skipped, 0 todo; tracked `dist/` clean.
- Approved/published/registry tarball SHA-256: `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`.
- npm integrity: `sha512-XIdt55Qm1wHAPSFQ9xAc/vWCs9WjIJVIjWYRhoK4THOt5fUsXrRU5IPMZgLmrgN0T8HU3aGE5Q36aZPzGyysCg==`.
- npm shasum: `3716c395fbd9e87fe7174511f6a6586d2026a661`.
- Registry tarball: https://registry.npmjs.org/@staticeng/opencode-litellm/-/opencode-litellm-0.2.0.tgz
- Registry inventory: 19 files, all mode `0644`, unpacked size 49,521 bytes.
- npm registry signature is present. Trusted-publishing provenance is absent because publication used the explicit user-approved credential fallback after the OIDC failure.
- Official OpenCode: `1.18.23`, binary SHA-256 `de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2`.
- Unversioned plugin reference installed `@staticeng/opencode-litellm@0.2.0` under an isolated OpenCode package cache.
- Seven representative strict-loopback probes passed, including GPT default/explicit/override, DeepSeek default/off, Qwen default/off, retired normal GPT-5.3 absence, and Spark presence.

## Reopen 1 Result

- Existing tag object and target were unchanged: `v0.2.0` -> `21f6583e9b4a112c0d2be79bbd102333de72bd89`.
- Protected `.npmjs` remained ignored and mode `0600`; it was not read, printed, copied, modified, or used.
- Fresh detached worktree was clean and contained the exact tagged commit.
- `npm ci`, build, 62/62 tests, and tracked-dist comparison passed.
- The clean-tag package inventory remained the expected 19 files.
- Clean-tag tarball SHA-256: `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`.
- Authorized reviewed SHA-256: `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`.
- Standard clean-checkout file modes were `0644`, while the earlier reviewed pack metadata recorded published-file modes as `0755`; this is the observed packaging difference, not a source change.
- No `npm publish` command ran. npm remains `latest=0.1.9`, with `0.2.0` absent.

## Release Identities

- Commit: `21f6583e9b4a112c0d2be79bbd102333de72bd89`
- Commit URL: https://github.com/jibanez-staticduo/opencode-litellm/commit/21f6583e9b4a112c0d2be79bbd102333de72bd89
- Annotated tag: `v0.2.0`; tag object `5fce7f28dc5710cbf3ce38c097125f590ff020ff`
- Release URL: https://github.com/jibanez-staticduo/opencode-litellm/releases/tag/v0.2.0
- CI URL: https://github.com/jibanez-staticduo/opencode-litellm/actions/runs/32964692665
- Publish workflow URL: https://github.com/jibanez-staticduo/opencode-litellm/actions/runs/32964753523
- npm package URL: https://www.npmjs.com/package/@staticeng/opencode-litellm

## Acceptance Criteria Coverage

- **T2-AC-1: PASS.** The independent review established the standard clean baseline, and Reopen 2 reproduced exact SHA-256 `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6` from a fresh unchanged tag checkout. Commit/push/CI/tracked-dist and 19-file inventory remain valid.
- **T2-AC-2: PASS.** Signed annotated tag `v0.2.0` dereferences to the release commit, and the published GitHub release has exact identity `v0.2.0` for package version `0.2.0`.
- **T2-AC-3: PASS by explicit user-approved exception.** The original trusted OIDC workflow reached provenance signing but failed registry authorization. Reopen 2 used the protected `.npmjs` fallback exactly once with tracing disabled and no credential disclosure or persistence. The published package has the npm registry signature but no trusted-publishing provenance.
- **T2-AC-4: PASS under the approved fallback contract.** npm reports published/latest `0.2.0` with exact integrity, shasum, tarball, 19-file inventory, all-file mode `0644`, and byte-identical SHA-256 `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`.
- **T2-AC-5: PASS.** Isolated official OpenCode `1.18.23` resolved unversioned `@staticeng/opencode-litellm` to installed `0.2.0` and passed seven representative behavior probes plus retirement/Spark catalog checks.
- **T2-AC-6: PASS.** Complete release, failure, fallback, registry, integrity, behavior, and rollback evidence is recorded here and in `.staticeng/evidences/TASK-2026-08-26-016-publish-opencode-litellm-020/logs/`.

## Verification

- Local clean install/build and full suite: 62 passed, 0 failed, 0 skipped, 0 todo.
- Historical nonstandard-mode candidate SHA-256: `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`; superseded for publication by the independently approved standard clean artifact.
- Published standard artifact and downloaded registry tarball SHA-256: `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6`.
- Package inventory: 19 files, limited to `LICENSE`, `README.md`, `package.json`, and `dist/*`.
- CI conclusion: success.
- Original OIDC workflow conclusion: failure at the final npm publish step after all repository gates passed.
- Reopen 2 authorized fallback conclusion: one successful publication of exact `0.2.0` tarball.
- Final npm state: published/latest `0.2.0` with verified registry integrity, signature, content, modes, and tarball checksum.
- `staticeng_validate` remains blocked by the governing workspace's pre-existing unrelated CodeMap backlog. Required repair dry-run was performed; apply was withheld because it proposed unrelated generated/runtime Markdown changes and still required broad manual module-boundary decisions.

## Rollback and Dist-Tag Guidance

Do not unpublish. Shared-client migration remains a separate PMA-gated task. If a release defect is discovered, stop rollout and prepare a patch release through a new approved SCR/task. If emergency containment is required before that patch, an authorized release operator may restore npm `latest` to `0.1.9`; do not move or recreate `v0.2.0`.

## Documentation Impact

No additional product or architecture documentation is required because release behavior did not change the already documented package contract. This evidence records the operational release and authorized fallback state.

## Open Risks

1. npm trusted-publishing authorization remains unresolved for future releases; Reopen 2 used a one-time credential fallback.
2. The published package has an npm registry signature but no trusted-publishing provenance because of the approved fallback path.
3. Shared clients have not migrated and must remain unchanged until their separate task is authorized.
4. The governing LiteLLM workspace has an unrelated pre-existing StaticEng CodeMap validation backlog.
