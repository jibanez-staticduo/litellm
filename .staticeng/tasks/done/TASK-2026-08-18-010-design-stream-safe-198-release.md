---
id: TASK-2026-08-18-010-design-stream-safe-198-release
complexity: standard
track: spec
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-010 - Design Stream-Safe 1.98.0 Release

## Overall Request Classification
- **complexity:** complex
- **track:** implementation
- **slice:** foundation
- **decomposition:** source logic implementation, focused QA, immutable image build, sequential NAS/Fedora deployment, and final verification/closure

## Objective
Produce an implementation-ready impact map and atomic slice plan for persisting both historical stream fixes on current `main` and safely deploying one LiteLLM 1.98.0 image to NAS and Fedora.

## Safety And Existing State
- Worktree is clean; `main` equals `origin/main` at `5daea54c93`.
- NAS is healthy on 1.92.0 and contains both uncommitted historical fixes.
- Fedora is healthy on 1.98.0 digest `sha256:2e947963...` but contains neither fix.
- Prior NAS 1.98.0 rollout failed because its host wrapper invoked obsolete runtime patches; the new release must remove that compatibility hazard before deployment.
- Spec/investigation only; do not edit source/runtime, build images, or restart services.

## Acceptance Criteria
- [ ] AC-1: Define exact source changes and focused regression tests for both ChatGPT-only stream guards while preserving non-ChatGPT behavior.
- [ ] AC-2: Define immutable build identity, rollback capture, and source-to-image verification requirements.
- [ ] AC-3: Define NAS wrapper migration/compatibility validation that removes obsolete host patch dependency without losing required startup behavior.
- [ ] AC-4: Define sequential deployment order, preservation checks, failure rollback gates, and host-specific topology constraints.
- [ ] AC-5: Define complete verification for unit/regression suites, health, inventory equality, native Responses, Codex, LazyMCP, routing/profile isolation, logs, and stable-tag promotion.
- [ ] AC-6: Return atomic specialist tasks with explicit dependencies and no concurrent shared-worktree implementation.

## Handoff
[Agent Message] From: product_manager To: technical_architect

Use the approved SCR, the completed stream-fix investigation, the Codex session `01a00b76-b1cb-7ab1-a4a2-ef1f08a002ba`, and current repository/runtime truth. Produce a minimal, implementation-ready slice plan. Do not mutate source or either host. Return a signed shared-contract handback with exact files/interfaces/tests and release gates.

## Architecture Review

### Impact Map And Contracts

The application change is limited to two existing Responses API extension points. No public API, schema, route, or new module is required

- `litellm/llms/custom_httpx/llm_http_handler.py`
  - In both `BaseLLMHTTPHandler.response_api_handler` and `async_response_api_handler`, capture whether the provider-transformed request requires native streaming before merging `extra_body`
  - After the merge, restore `data["stream"] = True` only when `custom_llm_provider == "chatgpt"` and the transformed request originally had `stream is True`
  - Preserve current precedence for every non-ChatGPT provider and do not force streaming when the ChatGPT transformation did not request it
- `litellm/llms/openai/responses/transformation.py`
  - In `OpenAIResponsesAPIConfig.should_fake_stream`, return `False` for `custom_llm_provider == "chatgpt"` after the existing `stream is True` guard and before capability lookup
  - Preserve capability-based fake streaming for every other provider
- `tests/test_litellm/llms/custom_httpx/test_llm_http_handler.py`
  - Add sync and async regressions proving `extra_body={"stream": False}` cannot override a ChatGPT provider-transformed `stream=True`
  - Add a non-ChatGPT control proving the same `extra_body` override remains effective
- `tests/test_litellm/llms/openai/responses/test_openai_responses_transformation.py`
  - Add a ChatGPT capability-miss regression proving `should_fake_stream(..., stream=True, custom_llm_provider="chatgpt")` is false
  - Add a non-ChatGPT control with `supports_native_streaming` returning false and prove fake streaming remains true
- Existing inheritance and provider behavior must remain covered by `tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py`

Affected maintained directories are `litellm/llms/custom_httpx/`, `litellm/llms/openai/responses/`, and their mirrored test directories. No maintained `.staticeng/codemap.yml` exists in those paths on current `main`; this task must not broaden into the known repository-wide CodeMap repair. If implementation creates or moves files, PMA must first create a separate CodeMap task

### Release And Wrapper Boundaries

- Build source of truth: clean `main` at the committed implementation SHA, with LiteLLM package version `1.98.0`
- Release orchestrator: `/home/staticduo/git/release-litellm.sh`. It currently pushes the stable tag before deployment and deploys both hosts without intervening verification. Do not use that path unchanged. Either harden it in a separate atomic task or execute an explicitly reviewed build-only/manual promotion procedure
- Immutable identity must include unique image tag, registry digest, image config digest/ID, architecture, package version, implementation commit SHA, and OCI revision/version labels. Build once, push once, resolve one digest, and deploy both hosts by that digest, not by a mutable tag
- Source-to-image proof must inspect the built image for version/revision labels and the two exact runtime guards, then run the focused regressions from the same clean commit before deployment
- NAS files affected outside this repository: `/volume2/docker/litellm/start-litellm.sh` and `/volume2/docker/litellm/docker-compose.yaml`
  - Remove startup invocation of `/app/patches/mcp_subject_token_optional.py`, `/app/patches/responses_bridge_drop_empty_params.py`, and the inline 1.92-only site-packages health patch
  - Preserve database fail-fast/readiness, guarded `source_url` compatibility repair, retry bounds, background repair behavior, `litellm "$@"`, config/data/auth mounts, one-password wrapper mount, healthcheck, networks, and service command
  - Remove the `/app/patches` bind mount only after the wrapper has no patch references. Keep host patch files as rollback artifacts until release closure
  - Back up wrapper and compose with mode 0600 and hashes. Validate `sh -n`, rendered Compose, no runtime source mutation references, target-image entrypoint/binary availability, and an isolated wrapper dry run before recreating production
- Fedora files are preservation-only: `fedora:/home/staticduo/docker/litellm/{.env,docker-compose.yaml,config.yaml,start-litellm.sh,onepassword-mcp-wrapper.sh,data/}`. Do not copy the NAS wrapper or topology to Fedora and do not alter its unrelated services or client configs

### Host-Specific Preservation Requirements

- NAS: preserve the exact 40-model inventory and all deployment IDs/settings; the eight public `gpt-*` aliases must retain default `chatgpt` primaries; eight account2, eight account3, and eight qualified default deployments must remain; `gpt-4o-mini-tts`, 32 unrelated rows, fallbacks, credentials, auth files, database, Redis, admin MCP services, volumes, networks, and dependency container identities must remain unchanged
- Fedora: preserve its current regular/account2 ChatGPT topology, matching bidirectional fallback rules and cross-profile policy, model/deployment inventory, credentials/auth files, database, Redis, admin MCP services, client configuration, ports, ulimits, volumes, networks, and unrelated services
- On both hosts, deployment is limited to `docker compose ... up -d --no-deps litellm`; no database restore, model mutation, dependency recreation, auth flow, or credential read is permitted

### Sequential Gates And Rollback

1. Preflight both hosts before build: capture sanitized image/digest/ID, health, restart/OOM state, exact normalized inventory and routing hashes, protected file hashes, dependency identities, auth-file presence/mode/mtime only, and tested host-local rollback image references. Capture a NAS wrapper/compose rollback pair
2. Implement and commit source plus tests. Run the two mapped test files, the inherited ChatGPT Responses test file, and repository `make check`. Stop on any failure
3. Build and push only a unique candidate tag from the clean commit. Resolve and pin the registry digest, verify source-to-image identity and architecture, and do not move the stable tag
4. Deploy Fedora first as the lower-risk image canary. Pull and recreate only `litellm` by digest. Verify every Fedora gate below. On failure, restore Fedora's captured image/env and verify rollback; NAS remains untouched
5. Back up and compatibility-test the NAS wrapper/compose migration, then deploy only NAS `litellm` by the same digest. On failure, restore the NAS image plus wrapper/compose as one rollback unit and verify 1.92.0 recovery; then restore Fedora to its pre-release image so the aborted release does not leave split image state
6. Compare both running containers to the same registry digest. Promote the stable private tag only after all source, host, topology, functional, log, and preservation gates pass; verify the stable tag resolves to that digest

Rollback is mandatory on unhealthy status, readiness/liveliness failure, restart growth, OOM, version/revision/digest mismatch, inventory/routing/config drift, missing account deployment, native Responses/Codex/LazyMCP failure, release-blocking log match, or dependency recreation. Do not promote stable on a waived or partial gate

### Verification Matrix

- Source: focused sync/async stream-override regressions, fake-stream provider controls, inherited ChatGPT Responses suite, and `make check`
- Image: package reports 1.98.0; OCI revision equals implementation SHA; unique tag, manifest digest, config digest/ID, and architecture agree; runtime introspection contains both guards
- Each host: running image equals pinned digest; readiness and liveliness HTTP 200; healthy, zero new restarts, `OOM=false`, stable over an observation interval; startup-only logs contain no patch, migration, schema, traceback, authentication prompt, `Stream must be set to true`, or release-blocking errors
- Inventory: exact pre/post normalized model/deployment equality and protected configuration hashes, plus the host-specific account/routing invariants above
- Native Responses: bounded no-retry valid list-input request with client `stream=false`/`extra_body.stream=false` completes without the ChatGPT stream error and emits the expected native Responses lifecycle
- Codex: one bounded Codex-compatible `/v1/responses` request per host passes without the stream error; record only status, model/deployment identity, and event/error classification
- LazyMCP: status plus bounded describe/list-tools and one harmless configured tool smoke pass independently on each host
- Routing/profile isolation: NAS representative public aliases select default-profile deployments while account2/account3 remain registered as fallbacks; Fedora regular and account2 representative requests select their matching deployments without cross-profile leakage or a new device-auth flow
- Final: both hosts still pass health, inventory, routing, Responses, Codex, LazyMCP, and clean-log checks after stable-tag promotion; registry stable resolution equals the candidate digest

### Atomic Specialist Tasks

1. **Source implementation, developer, implementation/logic**: modify only the two source files and two mapped test files above. Dependency: this architecture task. Exclusive shared-worktree implementation
2. **Source QA, QA engineer, investigation/qa**: independently run/review focused regressions, inherited suite, and `make check`; confirm ChatGPT-only scope and mutation-sensitive assertions. Dependency: task 1 committed; no source edits
3. **Release procedure hardening, developer or release engineer, implementation/foundation**: update `/home/staticduo/git/release-litellm.sh` or produce an approved manual equivalent so candidate push, sequential host gates, digest pinning, rollback, and delayed stable promotion are enforceable. Dependency: task 2. Must not deploy
4. **NAS wrapper migration preflight, developer, implementation/foundation**: back up and minimally migrate NAS wrapper/compose, perform isolated target-image compatibility validation, and stop before production recreation. Dependency: task 3 and pinned candidate digest. Fedora untouched
5. **Immutable build and source-to-image QA, developer then QA engineer, implementation/qa**: build once, push candidate only, record digest/labels/version/guard proof, and approve or reject the artifact. Dependency: tasks 2 and 3. No host deployment or stable promotion
6. **Fedora canary deployment, developer, implementation/foundation**: capture rollback/preservation baselines, deploy only Fedora `litellm` by digest, execute the full Fedora matrix, rollback on failure. Dependency: task 5
7. **NAS deployment, developer, implementation/foundation**: deploy only NAS `litellm` by the same digest using the validated wrapper, execute the full NAS matrix, and perform release-wide reverse rollback on failure. Dependency: tasks 4 and 6
8. **Cross-host QA and stable promotion, QA engineer then tech lead, investigation/qa and implementation/polish**: independently verify digest equality, all preservation and functional gates, then authorize and move stable to the verified digest. Dependency: tasks 6 and 7. Stable promotion is the only mutation in the final task

No two implementation tasks may concurrently use the shared LiteLLM worktree. Runtime tasks are strictly sequential in the dependency order above

### Technical Architect Review Note

AC-1 through AC-6 are design-covered by this impact map. No application source, image, tag, database, model, credential, wrapper, Compose file, or running service was changed during architecture review

`staticeng_validate` remains non-green only because of the pre-existing broken root links and repository-wide missing CodeMaps. The required repair dry run proposed hundreds of unrelated CodeMaps and Markdown normalizations, so it was not applied to this atomic spec task

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- AC-1 through AC-6 covered by the recorded impact map, contracts, host invariants, verification matrix, rollback gates, and eight-task decomposition.
- No runtime, image, source, wrapper, Compose, database, model, or credential mutation occurred.
- No steady-state product documentation update is required; this task is the technical truth anchor for implementation.
