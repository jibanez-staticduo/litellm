# TASK-2026-08-26-016 Evidence Summary

## Result

BLOCKED at the trusted npm publish gate. The exact reviewed 20-file candidate was committed and pushed, CI passed, and annotated tag/GitHub release `v0.2.0` were created. The release-triggered OIDC workflow passed identity, ancestry, build, 62 tests, tracked-dist, and pack checks, then npm rejected the publish PUT with HTTP 404. Per the task stop condition, no retry, dist-tag change, client migration, or isolated unversioned OpenCode probe was attempted.

## Release Identities

- Commit: `21f6583e9b4a112c0d2be79bbd102333de72bd89`
- Commit URL: https://github.com/jibanez-staticduo/opencode-litellm/commit/21f6583e9b4a112c0d2be79bbd102333de72bd89
- Annotated tag: `v0.2.0`; tag object `5fce7f28dc5710cbf3ce38c097125f590ff020ff`
- Release URL: https://github.com/jibanez-staticduo/opencode-litellm/releases/tag/v0.2.0
- CI URL: https://github.com/jibanez-staticduo/opencode-litellm/actions/runs/32964692665
- Publish workflow URL: https://github.com/jibanez-staticduo/opencode-litellm/actions/runs/32964753523
- npm package URL: https://www.npmjs.com/package/@staticeng/opencode-litellm

## Acceptance Criteria Coverage

- **T2-AC-1: PASS.** Preflight fetch confirmed local `main`, `origin/main`, and merge-base at `1e32745a9d30d3a83d37a37dc197b47c86fb5339`. Only the reviewed 20 implementation files were staged. Unrelated release-repository `.staticeng` artifacts remained unstaged. Commit `21f6583e9b4a112c0d2be79bbd102333de72bd89` was pushed non-force. CI passed all gates, tracked `dist/` is clean against the commit, and the package contains the expected 19 files.
- **T2-AC-2: PASS.** Signed annotated tag `v0.2.0` dereferences to the release commit, and the published GitHub release has exact identity `v0.2.0` for package version `0.2.0`.
- **T2-AC-3: FAIL/BLOCKED.** The existing release-only workflow used `id-token: write` and reached `npm publish --access public --provenance` without adding an npm secret or `.npmjs`. A Sigstore statement was signed, but the registry PUT returned HTTP 404, so trusted publication did not complete.
- **T2-AC-4: NOT MET.** npm still reports `latest=0.1.9`; version `0.2.0` is absent. No npm integrity, registry tarball, or completed package provenance exists for `0.2.0`.
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
