# TASK-2026-08-26-016 Evidence Summary

## Result

BLOCKED after Reopen 1 at the immutable-artifact checksum gate. The original release-triggered OIDC workflow failed with HTTP 404. During the user-authorized one-time `.npmjs` fallback, a fresh clean worktree of the unchanged `v0.2.0` tag passed install, build, 62 tests, tracked-dist, and 19-file inventory checks, but produced SHA-256 `2ac50fc9ab952c2ac244b73bcbe23eadf4b0fd530085e4a0c8d823749d7c82c6` instead of the authorized reviewed SHA-256 `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`. Publication stopped before any credential-backed command.

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

- **T2-AC-1: BLOCKED on clean-checkout reproducibility after initial PASS.** Commit/push/CI/tracked-dist and 19-file inventory remain valid, but the authorized tarball checksum does not reproduce from a standard clean worktree of the immutable tag.
- **T2-AC-2: PASS.** Signed annotated tag `v0.2.0` dereferences to the release commit, and the published GitHub release has exact identity `v0.2.0` for package version `0.2.0`.
- **T2-AC-3: FAIL/BLOCKED.** The existing release-only workflow used `id-token: write` and reached `npm publish --access public --provenance` without adding an npm secret or `.npmjs`. A Sigstore statement was signed, but the registry PUT returned HTTP 404, so trusted publication did not complete.
- **T2-AC-4: NOT MET.** The checksum mismatch stopped fallback publication. npm still reports `latest=0.1.9`; version `0.2.0` is absent. No npm integrity, registry tarball, or completed package provenance exists for `0.2.0`.
- **T2-AC-5: NOT RUN.** The required registry version was absent, so an unversioned official OpenCode resolution would necessarily resolve the prior `latest`. The stop condition prohibited continuing.
- **T2-AC-6: PASS for failure evidence and rollback guidance.** URLs, identities, candidate checksum, failure boundary, npm state, and rollback/dist-tag guidance are recorded here and in `logs/`.

## Verification

- Local clean install/build and full suite: 62 passed, 0 failed, 0 skipped, 0 todo.
- Reproduced candidate SHA-256 before and after commit: `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`.
- Package inventory: 19 files, limited to `LICENSE`, `README.md`, `package.json`, and `dist/*`.
- CI conclusion: success.
- Publish conclusion: failure at the final npm publish step after all repository gates passed.
- npm state after failure: published/latest `0.1.9`; `0.2.0` absent.
- `staticeng_validate` remains blocked by the governing workspace's pre-existing unrelated CodeMap backlog. Required repair dry-run was performed; apply was withheld because it proposed unrelated generated/runtime Markdown changes and still required broad manual module-boundary decisions.

## Rollback and Dist-Tag Guidance

Do not unpublish anything. Keep clients unchanged and do not begin the shared-client migration. `latest` correctly remains `0.1.9`, so no dist-tag rollback is needed. Treat the GitHub `v0.2.0` release as unusable until PMA coordinates correction of the npm trusted-publisher authorization/configuration. Do not reuse or move the existing tag. Any package-content correction requires a new patch release through an approved SCR/task; a pure external trusted-publisher correction may be handled only through PMA-authorized release recovery without changing the reviewed commit.

## Documentation Impact

No additional product or architecture documentation is required because release behavior did not change the already documented package contract. This evidence records the operational release state and blocker.

## Open Risks

1. The GitHub release exists while npm `0.2.0` does not; consumers must not infer npm availability from the GitHub release.
2. The npm trusted-publisher repository/workflow/environment authorization requires owner-side verification. The exact cause is not proven by the HTTP 404 alone.
3. Unversioned clients continue resolving `0.1.9`; migration remains blocked.
4. The governing LiteLLM workspace has an unrelated pre-existing StaticEng CodeMap validation backlog.
5. The authorized reviewed tarball checksum depends on packaging metadata that differs from a standard clean checkout, so publishing either artifact without a new explicit decision would violate the immutable-artifact gate.
