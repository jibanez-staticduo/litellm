# NAS LiteLLM Staging Clone Design

## Goal

Validate the NAS LiteLLM 1.98.0 release against a production-equivalent configuration and cloned database without changing the recovered production 1.92.0 runtime or the global OpenCode/Codex provider configuration.

## Isolation

The staging stack lives at `/volume2/docker/litellm-staging` and uses Compose project `litellm-staging`. It has distinct LiteLLM, PostgreSQL, and Redis containers, a private Compose network, independent database storage, and a loopback-only endpoint at `127.0.0.1:14000`. The staging LiteLLM container also joins the existing `llm-net` and `npm_npm-net` networks so copied MCP server definitions resolve exactly as they do in production.

## Production Parity

Copy `config.yaml`, `start-litellm.sh`, `onepassword-mcp-wrapper.sh`, `patches/`, and `data/` from `/volume2/docker/litellm`. Restore a fresh PostgreSQL custom-format dump into the staging PostgreSQL container. Reuse the production Redis credentials and application secrets only inside the isolated containers; do not print or commit them. Keep the global clients pointed at production throughout staging validation.

## Candidate

Run `docker.staticduo.com/litellm@sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`, built from application commit `2a8d1a60511730d32d6696936d901a6986583f78`. The legacy subject-token patch must return `not-needed` when the image already initializes the token.

## Validation

Require healthy status, zero restarts, `OOM=false`, LiteLLM 1.98.0, exact 40-model inventory parity, readiness/liveliness HTTP 200, successful structured Responses with a unique marker, LazyMCP tool discovery/call evidence, and startup logs without release-blocking errors. Production NAS and Fedora identities must remain unchanged during these tests.

## Promotion

After staging passes, back up the corrected production wrapper/patch, set production to the same immutable digest, recreate only the production `litellm` service with `--no-deps`, and repeat the same gates. Move `main-latest` only after production NAS passes. Keep staging until final verification succeeds, then remove it without touching production volumes.
