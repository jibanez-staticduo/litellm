# Fedora Deployment And Functional Gates

## Deployment

- Candidate: `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Final attempt: `final-20260819T023205Z`
- Protected rollback directory: `/home/staticduo/docker/litellm/releases/20260819-stream-safe-198-final/final-20260819T023205Z`
- Mutation: only the `LITELLM_IMAGE` selector
- Recreation: `docker compose ... up -d --no-deps litellm`
- Final container: `b4cff1ee704ccf7cb2d3f09d5890a467b3a77550fd7dd1f1e48ae631cf939b39`
- Started: `2026-08-19T02:32:15.989297648Z`
- Manifest/local ID on Fedora: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Architecture/version/revision: amd64 / 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`

An initial attempt automatically restored rollback after incorrectly expecting NAS's config image ID on Fedora. Fedora's Docker runtime stores this single-platform pull under the manifest digest. Rollback became healthy with HTTP 200 readiness/liveliness before the corrected host-specific identity check and final deployment

## Functional Gates

All requests used list input, `reasoning.context=all_turns`, effort `high`, summary `detailed`, `store=false`, encrypted reasoning inclusion, disabled parallel tool calls, and the Codex Responses Lite header

- Native account2 with client `stream=false`: HTTP 200 `text/event-stream`, nine ordered lifecycle events, exactly one `response.completed`, exact account2 selection
- Qualified regular: valid HTTP 200 SSE through the configured account2 fallback under the inherited primary quota disposition
- Direct account2: HTTP 200 `text/event-stream`, nine ordered lifecycle events, exactly one `response.completed`, exact account2 selection
- Public `gpt-5.6-sol`: HTTP 200 `text/event-stream`, nine ordered lifecycle events, exactly one `response.completed`, exact account2 fallback selection
- Stream-required/auth/device-flow/unsupported-value/unsupported-model failures: zero

Result: **DEPLOYMENT AND FUNCTIONAL GATES PASS**
