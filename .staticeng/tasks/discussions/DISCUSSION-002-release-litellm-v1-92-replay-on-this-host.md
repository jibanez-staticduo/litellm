---
id: DISCUSSION-002
title: "Release LiteLLM v1.92 replay on this host"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Release the current LiteLLM v1.92 replay branch to this host and verify it works locally.

## Purpose
The user asked whether the replayed LiteLLM v1.92 build can be released on this host and tested. PMA confirmed it is feasible, identified release-script caveats, proposed the exact release command, and received user approval to proceed.

## Repository Truth Relevant To This Discussion
- The old `main` was preserved before the upstream v1.92 replay in branch `backup-main-before-upstream-v1.92`.
- Local backup branch `backup-main-before-upstream-v1.92` points to `4f7364064d`.
- Remote backup branch `origin/backup-main-before-upstream-v1.92` also points to `4f7364064d`.
- `origin/main` was force-updated with `--force-with-lease` to the replay branch.
- Local `main` and `origin/main` both point to `29373e89c1`.
- Local `main` tracks `origin/main`.
- Local `main` was reported clean and up to date.
- `upstream/main` was reported at `79a6b8f7f0`.
- Current `main` was described as upstream intact plus 27 commits on top.
- `main...origin/main` had zero difference: `0 0`.
- This host has the LiteLLM stack at `/volume2/docker/litellm`.
- The current LiteLLM container on this host was reported healthy.

## Facts Established
- The user explicitly approved launching the release on this host.
- The release should build Docker from current `main` at `29373e89c1`.
- The release should push the built image to `docker.staticduo.com/litellm`.
- The release process is expected to create a rollback tag for the current image.
- The release process is expected to update `/volume2/docker/litellm/.env`.
- The release process is expected to run `docker compose pull/up -d litellm` for the local stack.
- Post-release validation should cover `/health/readiness`, container logs, and basic LazyMCP/MCP behavior.

## Requirements Captured
- Release the current LiteLLM replay build on this host.
- Use `/home/staticduo/git/litellm` as the production workdir for this release.
- Use `upstream` as `UPSTREAM_REMOTE`.
- Use `origin` as `FORK_REMOTE`.
- Use release tag `staticduo-gpt-lazymcp-v1.92-replay-20260707`.
- Run the release script with upstream merge disabled.
- Run the release script with Fedora deployment disabled.
- Verify the deployed service after release.

## Constraints
- Do not use the release script defaults blindly because `/home/staticduo/git/release-litellm.sh` defaults to the older workdir `/home/staticduo/git/litellm-production-main` and older remotes `fork/origin`.
- Do not perform an upstream merge as part of this release; the branch is already the replay result.
- Do not deploy to Fedora for this test; the user's request is to release and test on this host.
- Use `--no-fedora-deploy` to avoid touching Fedora.
- Use `--no-upstream-merge` to avoid changing the replayed branch before release.

## Non-Goals
- Do not deploy this release to Fedora during this workflow.
- Do not redo or alter the upstream replay unless a later task explicitly requests it.
- Do not use the old production workdir `/home/staticduo/git/litellm-production-main` for this release.
- Do not rely on default release-script remotes for this release.

## Decisions Made
- Proceed with release on this host after user approval.
- Use this command shape for the release:

```bash
PRODUCTION_WORKDIR=/home/staticduo/git/litellm \
UPSTREAM_REMOTE=upstream \
FORK_REMOTE=origin \
TAG=staticduo-gpt-lazymcp-v1.92-replay-20260707 \
/home/staticduo/git/release-litellm.sh --no-upstream-merge --no-fedora-deploy --tag staticduo-gpt-lazymcp-v1.92-replay-20260707
```

## Assumptions
- The release script honors `PRODUCTION_WORKDIR`, `UPSTREAM_REMOTE`, `FORK_REMOTE`, `TAG`, `--no-upstream-merge`, `--no-fedora-deploy`, and `--tag` as described by PMA.
- Docker registry access to `docker.staticduo.com/litellm` is available from this host.
- The local Docker Compose stack in `/volume2/docker/litellm` is the intended target for the host release.
- The current healthy container provides a valid rollback source image.

## Open Questions
- What exact LazyMCP/MCP basic checks should be run after deployment, beyond confirming a basic call succeeds?
- Should validation include real LiteLLM proxy calls to configured model aliases, or only readiness/log/MCP smoke checks?
- Should release evidence be captured under a new StaticEng task evidence directory, and what task ID should own it?

## Risks Or Concerns
- Running the release script without explicit environment overrides could target the wrong workdir or remotes.
- Running without `--no-fedora-deploy` could deploy to Fedora, which is outside this discussion's scope.
- Running without `--no-upstream-merge` could mutate or invalidate the replay state before testing.
- Deployment may update `/volume2/docker/litellm/.env`; any incorrect tag or registry push failure could affect the local running stack.
- LazyMCP/MCP behavior needs explicit validation because the release is a replay with 27 local commits on top of upstream.

## Referenced Files Or Areas
- `/home/staticduo/git/litellm`
- `/home/staticduo/git/release-litellm.sh`
- `/home/staticduo/git/litellm-production-main`
- `/volume2/docker/litellm`
- `/volume2/docker/litellm/.env`
- `docker.staticduo.com/litellm`
- `backup-main-before-upstream-v1.92`
- `origin/backup-main-before-upstream-v1.92`
- `origin/main`
- `upstream/main`
- `/health/readiness`
- LazyMCP/MCP smoke validation areas

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Execute the approved release command with the explicit safeguards, validate readiness/logs/LazyMCP/MCP behavior, capture evidence, and coordinate rollback if the host deployment fails.
