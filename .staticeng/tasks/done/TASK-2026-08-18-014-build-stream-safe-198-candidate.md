---
id: TASK-2026-08-18-014-build-stream-safe-198-candidate
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-014 - Build Stream-Safe 1.98.0 Candidate

## Objective
Capture complete pre-release baselines for NAS and Fedora, then build and push one immutable LiteLLM 1.98.0 candidate from clean commit `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa` without deploying or promoting stable.

## Safety
- Do not change either host's running image, wrapper, Compose, database, models, credentials, or services.
- Do not use `/home/staticduo/git/release-litellm.sh` unchanged because it promotes stable before host verification.
- Push only a unique candidate tag; do not move stable/latest tags.
- Stop if source is dirty, version/revision identity is wrong, preflight preservation baselines cannot be captured, or rollback images are unavailable.

## Acceptance Criteria
- [ ] AC-1: Capture sanitized NAS/Fedora image identity, health/restart/OOM, exact normalized inventories/routing hashes, protected-file hashes, dependency identities, account topology, and tested rollback references.
- [ ] AC-2: Build exactly once from clean committed `main` at `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`, package version 1.98.0, linux/amd64, with correct OCI revision/version labels.
- [ ] AC-3: Push only a unique immutable candidate tag and resolve manifest digest plus config digest/image ID; stable remains unchanged.
- [ ] AC-4: Source-to-image inspection proves both stream guards are embedded and the package reports 1.98.0 from the expected revision.
- [ ] AC-5: Focused source regressions pass against the committed source and bounded image-level import/introspection checks pass.
- [ ] AC-6: Evidence packet contains exact deployment digest, rollback references, preservation baselines, and a reviewed manual sequential gate procedure for Fedora then NAS.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-014-build-stream-safe-198-candidate/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Capture both host baselines, then build/push one candidate from the exact clean commit. Do not deploy, alter host files, or promote stable. Prove image identity and both guards. Return a signed AC-mapped handback and do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed.
- Candidate digest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`.
- Config digest: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`.
- Built once from clean commit `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`; stable remained unchanged.
- No host deployment or file mutation occurred.

## QA Engineer: Post Implementation Expectations
- Independently approved Fedora canary deployment by immutable digest.
- Confirmed 1.98.0, linux/amd64, expected revision, both embedded guards, and 146 passing tests with no failures/skips.
- Confirmed stable tag and both host runtimes remained unchanged.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 passed with sanitized evidence under `.staticeng/evidences/TASK-2026-08-18-014-build-stream-safe-198-candidate/`
- Exactly one `linux/amd64` candidate was built from clean commit `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa` and pushed once
- Immutable deployment reference is `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`; config digest/image ID is `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Package 1.98.0, OCI revision/version, `linux/amd64`, and both stream guards were verified from the image
- NAS and Fedora were not deployed or edited; both remained healthy with unchanged image/protected-file identities
- Stable/latest was not moved and remains on manifest digest `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- No product documentation or CodeMap update is required because this task changed no source or steady-state architecture
