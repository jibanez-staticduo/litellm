---
id: DISCUSSION-002
title: "Deploy LiteLLM cachecodecfix image to Fedora"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Deploy the LiteLLM cachecodecfix image to Fedora after confirming the prior release was local-only.

## Purpose
Capture the user's request to update LiteLLM on Fedora and preserve the deployment context, constraints, and StaticEng metadata issue from the preceding release discussion.

## Repository Truth Relevant To This Discussion
- The previous release/deploy activity was not blocked by LiteLLM functionality or by the release artifact; the reported failure was from StaticEng metadata validation.
- The release command was explicitly run with `--no-fedora-deploy`.
- The previous release updated only the local host/NAS stack under `/volume2/docker/litellm`.
- The local image/tag after the release was `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
- Fedora was not touched during that release and should still be running whatever LiteLLM image/version it had before.

## Facts Established
- StaticEng validation reported broken links in `.staticeng/codemap.yml`:
  - `Agents_Common.md` does not exist.
  - `docs/core/agent_orchestration.md` does not exist.
  - `docs/architecture/TECHNICAL_ARCHITECTURE.md` does not exist.
  - Those paths also violate StaticEng's Rule of Local Knowledge.
- StaticEng also reported many missing `codemap.yml` files because source directories lack CodeMaps.
- Affected unmapped areas explicitly mentioned include `examples`, `docker`, `scripts`, `litellm`, `litellm/responses`, and multiple `litellm/llms/...` paths.
- The large number of missing CodeMaps is due to replaying/importing the full upstream repository while StaticEng expects many source directories to be mapped.
- `staticeng_repair` was run in dry-run during the release.
- `staticeng_repair` proposed creating many CodeMaps throughout the repository.
- The repair was not applied because it would create a large metadata diff unrelated to the cachecodecfix release/deploy work.
- The user asked whether LiteLLM had been updated on Fedora.
- Product Manager confirmed Fedora was not updated.
- The user then requested that LiteLLM be updated on Fedora.

## Requirements Captured
- Deploy/update LiteLLM on Fedora using the cachecodecfix release image/tag unless a later task identifies a newer approved image.
- Treat the Fedora update as new work because the prior release was explicitly local-only.
- Preserve the separation between functional LiteLLM deployment work and broad StaticEng metadata cleanup.
- If StaticEng metadata validation issues appear during Fedora deployment, do not assume they indicate a LiteLLM deployment failure.

## Constraints
- Do not apply broad `staticeng_repair` CodeMap creation as part of the Fedora deploy unless PMA explicitly scopes that metadata cleanup into the task.
- Avoid introducing a large StaticEng metadata-only diff into the LiteLLM Fedora deployment work.
- Respect that the known StaticEng errors are unrelated to the LiteLLM release artifact.
- The target Fedora environment's current LiteLLM image/version was not established in the transcript and must be checked before changing it.

## Non-Goals
- Do not fix all broken StaticEng CodeMap links as part of this discussion summary.
- Do not generate missing CodeMaps across the full repository as part of the Fedora deploy summary.
- Do not treat the previous local/NAS deployment as evidence that Fedora has already been updated.
- Do not re-run or broaden the prior local-only release unless required by the deployment task.

## Decisions Made
- The previous StaticEng validation issue is classified as StaticEng metadata debt, not a LiteLLM functional or release failure.
- Broad StaticEng metadata repair should be handled in a separate task.
- Fedora still needs a LiteLLM update because the prior release used `--no-fedora-deploy`.

## Assumptions
- The intended Fedora deployment candidate is `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`, because it was the final local image/tag from the prior release.
- The Fedora host has an existing LiteLLM deployment mechanism or stack that later agents can inspect and update.
- The user wants Fedora updated now, not merely a plan for a future update.

## Open Questions
- What exact host, path, compose file, service name, or deployment mechanism controls LiteLLM on Fedora?
- What LiteLLM image/tag is Fedora currently running?
- Should the Fedora deployment use the confirmed local tag `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`, or is there a newer approved tag?
- What health checks or smoke tests are required after updating Fedora?
- Are credentials, registry access, or remote SSH details already available to the implementation agent through approved tooling?

## Risks Or Concerns
- Deploying the wrong image could roll Fedora forward to an unintended version or miss the cachecodecfix.
- StaticEng metadata failures could distract from deployment verification if they are not explicitly separated from functional LiteLLM checks.
- Applying broad StaticEng repair during deploy would create a large unrelated diff and complicate review.
- Fedora's current state is unknown from the transcript, so the deployment agent must inspect before modifying.
- Remote deployment may require credentials or host access not captured in the transcript.

## Referenced Files Or Areas
- `.staticeng/.config/runtime/discussions/DISCUSSION-002-transcript.md`
- `.staticeng/tasks/discussions/DISCUSSION-002-deploy-litellm-cachecodecfix-image-to-fedora.md`
- `.staticeng/codemap.yml`
- `Agents_Common.md`
- `docs/core/agent_orchestration.md`
- `docs/architecture/TECHNICAL_ARCHITECTURE.md`
- `examples`
- `docker`
- `scripts`
- `litellm`
- `litellm/responses`
- `litellm/llms/...`
- `/volume2/docker/litellm`

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Coordinate a scoped implementation task to inspect Fedora's current LiteLLM deployment, update it to the approved cachecodecfix image, verify runtime health, and keep unrelated StaticEng metadata cleanup out of the deploy path.
