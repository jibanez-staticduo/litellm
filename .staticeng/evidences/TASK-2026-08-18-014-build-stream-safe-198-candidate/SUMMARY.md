# Stream-Safe 1.98.0 Candidate Evidence

## Summary

Captured sanitized preservation and rollback baselines for NAS and Fedora, passed focused source regressions, and built exactly once from a clean detached worktree at the required commit. Pushed exactly one unique candidate tag without deployment or stable/latest promotion

## Work Performed

- Captured image, health, restart/OOM, inventory, routing, protected-file, dependency, auth metadata, account topology, and tested rollback identity for both hosts
- Ran the three focused mapped/inherited suites with 146 passes and no failures or skips
- Built one `linux/amd64` image with OCI revision/version labels from clean commit `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Pushed one unique candidate tag and resolved its manifest and config digests
- Imported the installed image package, verified version 1.98.0, and proved both native-stream handler guards plus the fake-stream bypass are embedded
- Confirmed both hosts and the stable tag remained unchanged after build/push
- Reviewed and recorded the strict Fedora-then-NAS deployment, rollback, verification, and delayed-promotion procedure

## Acceptance Criteria Coverage

- **AC-1: PASS**. `logs/02-nas-preflight.log` and `logs/03-fedora-preflight.log` contain sanitized image/health, exact normalized inventory and router hashes, protected hashes, dependency identities, account topology, auth metadata, and tested rollback references
- **AC-2: PASS**. `logs/01-source-and-tests.log` and `logs/04-build-and-image-verification.log` prove one build from clean committed `main` revision `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`, package 1.98.0, `linux/amd64`, and matching OCI labels
- **AC-3: PASS**. Only the unique candidate tag was pushed. The manifest digest is `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, config digest/image ID is `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`, and stable remained `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- **AC-4: PASS**. Image import/introspection reports package 1.98.0, expected OCI revision, and all three committed runtime guard locations embedded. See `logs/04-build-and-image-verification.log`
- **AC-5: PASS**. The committed source suite passed 146 tests with no failures or skips, and bounded image import/version/callable introspection passed. See `logs/01-source-and-tests.log` and `logs/04-build-and-image-verification.log`
- **AC-6: PASS**. This packet includes the immutable deployment digest, both rollback digests, preservation baselines, postflight non-mutation proof, and reviewed manual sequential gate in `logs/05-sequential-deployment-gate.md`

## Documentation Impact

No steady-state product or architecture documentation update is required. This task evidence records the release artifact and operational gate truth. No source/module navigation changed, so no CodeMap update is required

## Open Risks

The candidate is not production-validated until the separate Fedora and NAS deployment tasks execute the full runtime matrix. NAS still requires the separately scoped wrapper/Compose migration and a fresh mode-0600 rollback pair before any mutation. `staticeng_validate` remains blocked by pre-existing broken root links and repository-wide missing CodeMaps; its broad repair dry run was reviewed but not applied. See `logs/07-staticeng-validation.log`

## Recommended Next Step

PMA should hand the immutable candidate to independent image QA, then authorize the Fedora canary task using the reviewed digest-pinned gate. NAS must remain untouched until Fedora passes and the NAS wrapper migration preflight is complete
