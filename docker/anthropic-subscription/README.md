# Claude Code subscription gateway

This NAS pilot keeps Anthropic OAuth login and refresh in Claude Code and records API-equivalent usage in an isolated LiteLLM database. It listens on `127.0.0.1:14001`, has no Anthropic API credentials or fallback models, and uses manual Docker lifecycle control

Copy `compose.yaml` and `config.yaml` to the private deployment directory `/volume2/docker/litellm-anthropic-subscription`. Initialize a new `postgresql-data` directory owned by UID 1001. Keep existing data directories intact

Supply PostgreSQL passwords, `DATABASE_URL` and `LITELLM_MASTER_KEY` through a private Compose override named `compose.credentials.yaml`, readable only by the owner. PostgreSQL needs `POSTGRESQL_PASSWORD` and `POSTGRESQL_POSTGRES_PASSWORD`. The database URL names the `postgres` service and `litellm_subscription` database. Do not add `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` to either service

Build the candidate image from a small context containing only this Dockerfile, `litellm/proxy/anthropic_endpoints/endpoints.py` as `endpoints.py`, `litellm/llms/anthropic/count_tokens/handler.py` as `handler.py`, and the repository's `model_prices_and_context_window.json`. Set `ANTHROPIC_SUBSCRIPTION_IMAGE` to the resulting immutable image ID in `image.env`. The base image is the verified NAS release, not a floating tag

```bash
docker compose --env-file image.env -f compose.yaml -f compose.credentials.yaml config --quiet
docker compose --env-file image.env -f compose.yaml -f compose.credentials.yaml up -d
curl --fail http://127.0.0.1:14001/health/readiness
```

Create a virtual key restricted to the three configured aliases. Give Claude Code that key in a separate custom header while preserving its saved claude.ai login

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:14001
export ANTHROPIC_CUSTOM_HEADERS="x-litellm-api-key: Bearer $LITELLM_CLAUDE_KEY"
export ANTHROPIC_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-5-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
claude
```

The session must have no active `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper`. A custom header authenticates to LiteLLM without replacing Claude Code's subscription credential. Do not copy OAuth tokens into the proxy. Canonical model names preserve Claude Code's native capabilities and context metadata

The NAS installation includes the dedicated `~/.local/bin/claude-litellm` launcher from this directory. Run `claude-litellm` on the NAS to use the gateway with the existing subscription login. It reads the restricted key from the private runtime directory and sets the URL and model variables only for its child process. Existing Claude settings and login remain available to the ordinary `claude` command. The launcher rejects inherited API credentials; do not add an `apiKeyHelper` to this profile

Verify a streamed conversation, a tool result in a subsequent turn, native token counting and spend logs with `used_client_oauth_token=true`. Cost is the equivalent API value, not an Anthropic invoice. Verify an unauthenticated upstream request fails without fallback. An OAuth flag or HTTP readiness alone does not prove a successful subscription request

Stop the pilot with `docker compose --env-file image.env -f compose.yaml -f compose.credentials.yaml stop`. Use the ordinary `claude` command to restore direct client routing, preserving its login and all database data

## Verified deployment, 2026-10-01

The candidate image `sha256:1262f02dcc48bbc4cc9728a03a51a75661845b42000ca8c81df87157d70e28d8` contains the token-counting fix from `d17375a5a9`. The NAS proxy and dedicated PostgreSQL are healthy with manual restart policy. The existing shared LiteLLM instance was not restarted

Claude Code 2.1.285 displayed `Sonnet 5.5 with high effort` and `Claude Pro`. An interactive streamed turn read `subscription-probe.txt` and returned `SUBSCRIPTION_TOOL_OK`. The next turn returned `SUBSCRIPTION_TOOL_OK` and `CONTINUATION_OK` without another read. `/context` completed and native token-counting requests returned HTTP 200. Separate native client requests confirmed Opus 5.5 and Haiku 4.5 access

A real native token-counting request returned `{"input_tokens":18}`. Invalid OAuth returned HTTP 401 `authentication_error`. A Messages request with only the restricted proxy key also returned HTTP 401. No fallback models or Anthropic API credentials are configured

Requests `msg_011Cfbn3woLuuNZNUKAir5Lh`, `msg_011Cfbn43xBkqfoTuu7twBdT` and `msg_011Cfbn47rLSiVhqwsM6EsT8` recorded OAuth attribution and API-equivalent spend of USD `0.018318`, `0.0015432` and `0.0022766`. Recalculation with the deployed LiteLLM cost function matched all three amounts. The records include one-hour cache creation, cache reads and reasoning tokens. Raw OAuth, refresh, virtual and master credentials were absent from the inspected container logs and spend rows

The endpoint and handler regressions pass 48 focused tests, including upstream 401/429, alias authorization and destination isolation. Independent review found no blocking defect. The integrated `make check` gate passes, including type, lint, budget and OpenAPI/dashboard schema checks. The dashboard endpoint `/spend/logs/ui` returns the verified request and spend. Forced live quota exhaustion and interruption during generation were not exercised; status preservation and absence of local fallback are covered by the focused regressions

See the [implementation plan](../../docs/superpowers/plans/2026-10-01-anthropic-subscription.md) for acceptance and the separate scope of future central account management
