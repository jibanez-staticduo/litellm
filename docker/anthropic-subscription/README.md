# Claude Code subscription gateway

The current flow uses native Claude Code with two account profiles, selected by LiteLLM. Native Claude Code owns login and credential renewal on Fedora. LiteLLM reads credentials and records API-equivalent usage. The earlier HTTP and Agent SDK experiments are recorded below as historical evidence

## Native Claude Code accounts

`native-client-models.json` defines three neutral aliases and three explicit aliases per account. The neutral `claude-sonnet-5-5`, `claude-opus-5-5` and `claude-haiku-4-5` aliases initially select `staticduo`. Prefix an alias with `claude-staticduo/` or `claude-defend1/` to select that account explicitly

Each deployment selects `anthropic_execution_mode=native_client`, `anthropic_credential_mode=claude_code` and `use_anthropic_oauth=true`. The proxy preserves the native Messages body and headers, replaces authorization with the selected account's access token and aligns the account UUID in native request metadata. Messages and their native count endpoint support this mode. Chat Completions, Responses and the generic token counter reject it

Fedora mounts `~/.claude-homes` read-only. The NAS uses access snapshots described in `native-profiles/README.md`. Only access tokens and the required account identity reach those snapshots. The proxy reads both sources without writing credentials or renewing them. Run `claude_staticduo` or `claude_defend1` on Fedora to let native Claude renew its profile, then synchronize NAS access. An expired profile returns an authentication error

The Fedora selector extends the existing signed journal and lock. Run `litellm_fallbacks claude --status`, `litellm_fallbacks claude staticduo` or `litellm_fallbacks claude defend1`. A switch changes only the neutral aliases' `anthropic_auth_profile` on Fedora and NAS. Explicit account aliases, ChatGPT routing and fallback arrays stay intact. `deploy/quota-sidecar/anthropic-primary.patch` and its manifest contain the reviewed controller changes

`claude_litellm` starts the native client through each host's shared proxy. The NAS launcher synchronizes access snapshots before launch. `claude_usage` displays five-hour and weekly percentages, reset times and the extra usage state for both accounts. `claude_usage --json` provides the same data in a sanitized versioned format. These commands do not enable extra usage or perform inference

The isolated candidate passed real native Read-tool and resume checks with Sonnet, and Read-tool checks with Opus and Haiku. Shared Fedora and NAS passed native Read-tool and resume checks. Both hosts' spend records carry the selected account and server OAuth attribution, and their costs match the deployed LiteLLM calculator. At validation, `defend1` had exhausted its weekly quota and both accounts reported extra usage disabled. Successful inference on that account requires quota availability

## Earlier Shared Deployment

`shared-models.json` is the deployment template for `claude-sonnet-5-5`, `claude-opus-5-5` and `claude-haiku-4-5`. They are visible to team `49cfd117-ef74-4eec-b26e-2d2ff083f5be` through its `all-proxy-models` access. Each deployment has the deliberately invalid sentinel `sk-ant-oat01-client-oauth-required` rather than a usable server credential. Its subscription metadata describes the intended use and does not enforce an immutable server policy. The inspected shared configuration has no global Anthropic API credential or fallback for these aliases, and header forwarding is limited to their model groups

Generate the current overlay context with `build-context.sh`, passing an empty directory. It copies the provider, authenticator, OAuth policy, router, proxy and Responses files required by this Dockerfile, plus the repository price map. The base image is pinned to `sha256:7263f32613a930e539792b7a1613a02eef617846d8e8ae493ab779a475af9fba`

```bash
docker/anthropic-subscription/build-context.sh "$ANTHROPIC_BUILD_CONTEXT"
docker build -t litellm-anthropic-candidate "$ANTHROPIC_BUILD_CONTEXT"
```

```bash
curl --fail https://litellm.staticduo.com/health/readiness
```

The verified phase 1 overlay was `sha256:e941ad3d6c58aa1f7a136a0a21e542eef3a96bc911ab5e672efdf40ad2cf6316`, containing the counter fix `d17375a5a9` and Responses replay fix `cb61cd4156`. It was selected through `LITELLM_IMAGE` in `/volume2/docker/litellm/.env`. The previous environment is backed up privately at `/volume2/docker/litellm/anthropic-subscription/environment.before-overlay`. Activation recreated only `litellm` with Compose `up -d --no-deps --pull never`. The shared container was healthy and readiness returned HTTP 200. This image evidence predates the managed-profile candidate

## Claude Code passthrough client

Use a virtual key restricted to the three configured aliases. Give Claude Code that key in a separate custom header while preserving its saved claude.ai login

```bash
export ANTHROPIC_BASE_URL=https://litellm.staticduo.com
export ANTHROPIC_CUSTOM_HEADERS="x-litellm-api-key: Bearer $LITELLM_CLAUDE_KEY"
export ANTHROPIC_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-5-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
claude
```

The session must have no active `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper`. A custom header authenticates to LiteLLM without replacing Claude Code's subscription credential. Do not copy OAuth tokens into the proxy. Canonical model names preserve Claude Code's native capabilities and context metadata

The NAS installation includes the dedicated `~/.local/bin/claude-litellm` launcher from this directory. Run `claude-litellm` on the NAS to use the shared HTTPS gateway with the existing subscription login. It reads the restricted key from `/volume2/docker/litellm/anthropic-subscription/claude-code-key`, overridable with `LITELLM_CLAUDE_KEY_FILE`, and sets the URL and model variables only for its child process. Existing Claude settings and login remain available to the ordinary `claude` command. The launcher rejects inherited API credentials; do not add an `apiKeyHelper` to this profile

Verify a streamed conversation, a tool result in a subsequent turn, native token counting and spend logs with `used_client_oauth_token=true`. Cost is the equivalent API value, not an Anthropic invoice. Verify an unauthenticated upstream request fails without fallback. An OAuth flag or HTTP readiness alone does not prove a successful subscription request

Use the ordinary `claude` command to restore direct client routing while preserving its login. A shared image rollback restores the previous `LITELLM_IMAGE` from the private environment backup and recreates only `litellm`. Keep pilot database files and private credentials intact when removing temporary containers

## Managed native profiles

`managed-models.json` defines `claude-sonnet-5-5-subscription`, `claude-opus-5-5-subscription` and `claude-haiku-4-5-subscription`. Each deployment enables `use_anthropic_oauth`, fixes `anthropic_auth_profile=default`, selects `anthropic_execution_mode=native_sdk` and disables retries. The provider remains Anthropic, with the existing Chat and Responses bridges

The internal broker runs the pinned official Agent SDK. Authorize each account in its own `CLAUDE_CONFIG_DIR` through `claude auth login --claudeai`. Keep that directory at 0700 and its credential file at 0600. Mount the parent account directory as `/profiles`, so profile `default` uses `/profiles/default` and HOME `/profiles/default/home`. Native Claude Code owns refresh. The proxy does not import, export or independently refresh this authorization. NAS and Fedora need independent logins

Build the broker from this directory with `Dockerfile.native-sdk`. `compose.native-sdk.yaml` adds the internal broker to the isolated proxy project. Set `ANTHROPIC_NATIVE_SDK_IMAGE` to its reviewed image, `ANTHROPIC_NATIVE_SDK_PROFILE_ROOT` to the private account directory and `ANTHROPIC_NATIVE_SDK_KEY` to a separate random service credential. The proxy uses `ANTHROPIC_NATIVE_SDK_BASE_URL` and the same service credential. Keep this broker on the private Docker network. Its credential is distinct from subscription OAuth and the client's LiteLLM key

```bash
docker build -f docker/anthropic-subscription/Dockerfile.native-sdk \
  -t litellm-anthropic-native-sdk docker/anthropic-subscription
```

LiteLLM stamps authenticated key ownership and the selected deployment. The broker binds sessions to owner, profile, deployment and model. Client metadata and headers cannot select another account or native session. History prefixes, tool IDs and results must match the native conversation. Thinking signatures and caller tool names survive the protocol translation. Built-in SDK tools are disabled; the caller executes its own tools

The count route uses native SDK refresh, then the official token-counting endpoint with the engine-owned access credential. It counts the supplied body without paid inference or a local estimate. Credentials stay inside the broker. Unsupported API controls fail explicitly instead of being silently ignored

The earlier direct HTTP authenticator remains available for explicit HTTP deployments. Its managed stores are separate from native profiles. The experimental `claude_code` HTTP compatibility preset does not run the SDK and did not establish OpenCode subscription-only support. Preserve the previous private configuration for rollback instead of sharing refresh tokens between both modes

## Managed clients and accounting

The dedicated `codex-anthropic-litellm` and `opencode-anthropic-litellm` launchers read a restricted virtual proxy key from `~/.config/litellm/anthropic-proxy-key`, overridable with `LITELLM_ANTHROPIC_KEY_FILE`. Keep that file at mode 0600. Set the proxy root URL through `LITELLM_ANTHROPIC_URL` or the local file `~/.config/litellm/anthropic-proxy-url`, without `/v1`. There is no default host. These files contain the proxy key and destination, never subscription OAuth credentials

Install the executable launchers in a directory on the client's PATH. They preserve existing logins, provider configuration and policy settings. They export `LITELLM_ANTHROPIC_QA_KEY` only to the child client and leave upstream OAuth to the managed server profile. Neither launcher changes the ordinary `codex` or `opencode` defaults

The Codex launcher supplies the `anthropic_subscription` provider through command-line configuration with `base_url=<root>/v1`, `env_key=LITELLM_ANTHROPIC_QA_KEY` and `wire_api=responses`. It defaults to `claude-sonnet-5-5-subscription`, overridable with `LITELLM_ANTHROPIC_MODEL` or ordinary Codex arguments. It disables hosted web search for this provider because the broker only supports caller tools. External MCP search tools remain available. It sets `mcp_optional_startup_grace_ms=0` to wait for each optional MCP server's configured startup timeout before sending the first request or resuming. This avoids dropping tools from an existing native conversation while a server starts. User arguments are passed through without changing approval or sandbox policy

```bash
codex-anthropic-litellm
codex-anthropic-litellm exec "Inspect the current project"
```

The OpenCode launcher passes arguments directly to `opencode`. Configure its separate `subscription` provider in the host's existing runtime config with `npm=@ai-sdk/anthropic`, `options.baseURL=<root>/v1`, `options.apiKey={env:LITELLM_ANTHROPIC_QA_KEY}` and the managed aliases in `models`. Match that base URL to the launcher's selected root. The launcher does not rewrite provider configuration or choose a global default model

```bash
opencode-anthropic-litellm run --model subscription/claude-sonnet-5-5-subscription "Inspect the current project"
```

Codex uses LiteLLM's `/v1/responses` bridge and OpenCode uses `/v1/messages`. These launchers do not add an Anthropic catalog to Codex or enable native Anthropic Responses support

These routes reuse the Anthropic provider and Responses bridge, including signed thinking replay. The direct HTTP candidate passed Codex but failed OpenCode. The native broker passes Codex tool use and resume. Its standalone probes with the original OpenCode system prompt and parallel tools did not establish support for the complete OpenCode agent request, which Anthropic rejects

Spend remains an API-equivalent valuation derived from provider usage and the effective LiteLLM price map. It is not an Anthropic API invoice. For phase 1 passthrough, verify `used_client_oauth_token=true`. Managed profiles instead require `used_client_oauth_token=false`, server OAuth attribution and the configured profile. For the default profile, the expected ledger values are `used_server_oauth_token=true` and `anthropic_auth_profile=default`. The HTTP candidate ledger correction passed live verification; native broker accounting must pass the same checks. Verify the served model, virtual key attribution and cache usage, and verify rejected authentication records no successful generation spend

## Verified phase 1 shared route, 2026-10-01

The authenticated shared catalog contains all three aliases for the restricted virtual key. `/model/info` contains all three deployments for the requested team. The final NAS launcher used Read and returned `SUBSCRIPTION_TOOL_OK`; a second turn through `--resume` returned `FINAL_ROUTE_817` with exit code 0 and `is_error=false`

The shared native counter returned HTTP 200 with `{"input_tokens":11}`. Invalid OAuth and a request without OAuth each returned HTTP 401. The separate candidate QA route completed Read and a continuation, with counter HTTP 200 and invalid or absent OAuth HTTP 401

The shared dashboard API `/spend/logs/ui` returned HTTP 200 for `key_alias=claude-subscription`, `model_group=claude-sonnet-5-5` and the UTC interval `2026-10-01 17:27:36` to `2026-10-02 00:00:00`. The last four native successful records have `used_client_oauth_token=true` and API-equivalent spend of USD `0.0080198`, `0.0103398`, `0.0112836` and `0.0779932`. The request without OAuth recorded zero spend. The calculator comparison was performed on the pilot, not repeated on the shared records

The Responses patch passes 112 focused tests and the counter passes 48 focused tests. `make check` passes for the Responses patch, and independent review findings were corrected. These earlier checks belong to phase 1 and do not establish managed-client compatibility

Temporary QA `litellm-anthropic-qa` and pilot containers `litellm-anthropic-subscription-proxy-1` and `litellm-anthropic-subscription-postgres-1` were stopped and removed without `-v`. Their absence was verified with `docker ps -a`. Pilot `postgresql-data` and private files remain intact. The private pilot directory has mode 700 and its key, config, credentials and image files have mode 600 after correcting inherited ACL permissions. The native phase 1 shared `litellm` container remains healthy on its verified image. The later direct HTTP candidate containers were also removed after their checks

## Initial isolated pilot evidence

Claude Code 2.1.285 displayed `Sonnet 5.5 with high effort` and `Claude Pro`. An interactive streamed turn read `subscription-probe.txt` and returned `SUBSCRIPTION_TOOL_OK`. The next turn returned `SUBSCRIPTION_TOOL_OK` and `CONTINUATION_OK` without another read. `/context` completed and native token-counting requests returned HTTP 200. Separate native client requests confirmed Opus 5.5 and Haiku 4.5 access

A real native token-counting request returned `{"input_tokens":18}`. Invalid OAuth returned HTTP 401 `authentication_error`. A Messages request with only the restricted proxy key also returned HTTP 401. No fallback models or Anthropic API credentials are configured

Requests `msg_011Cfbn3woLuuNZNUKAir5Lh`, `msg_011Cfbn43xBkqfoTuu7twBdT` and `msg_011Cfbn47rLSiVhqwsM6EsT8` recorded OAuth attribution and API-equivalent spend of USD `0.018318`, `0.0015432` and `0.0022766`. Recalculation with the deployed LiteLLM cost function matched all three amounts. The records include one-hour cache creation, cache reads and reasoning tokens. Raw OAuth, refresh, virtual and master credentials were absent from the inspected container logs and spend rows

The pilot dashboard endpoint `/spend/logs/ui` returned the verified request and spend. Forced live quota exhaustion and interruption during generation were not exercised. Status preservation and absence of local fallback are covered by the focused regressions

## Isolated managed candidate evidence

Candidate 04 passed Messages for all three managed models, Chat Completions, Responses, both tested token-counting routes and signed thinking replay through a tool continuation. Its NAS authorization is independent of the native login, stored under private directory mode 0700 and credential mode 0600. A real refresh rotated the credential successfully. Fedora has a separately imported authorization, but the managed candidate is not deployed there

Final candidate 05, `sha256:875fba7af1d4cdec0f0967e73f9016688f2b1fd563a81ffc597603f711e114fa`, repeats those API checks after the accounting correction. All 21 overlay source files match the checkout byte for byte. Five successful spend records preserve `used_server_oauth_token=true`, `used_client_oauth_token=false`, `anthropic_auth_profile=default` and the restricted virtual key alias. Recalculation with the deployed price map matches each recorded amount

Codex 0.159.2 passed tools, file handling and resume on the isolated candidate, with 207 reasoning tokens reported. This evidence uses the Responses bridge and does not add native Anthropic catalog metadata to Codex

OpenCode 2.0.20 received HTTP 400 from Anthropic on both Messages and Responses:

> Third-party apps now draw from your extra usage, not your plan limits. Add more at claude.ai/settings/usage and keep going

The retry used `drop_params: true` only in the pilot to handle OpenCode's `prompt_cache_key`; the provider rejection remained. OAuth `GET /api/oauth/usage` reported `extra_usage.is_enabled=false` and `credits_ever_enabled=false`. This is an external blocker for subscription-only OpenCode. Extra usage is not enabled by this deployment, and the candidate is not promoted to Fedora or NAS

## Remaining work

Managed profile custody, explicit account selection and serialized refresh are implemented, with real refresh verified in isolation. Automatic account rotation and quota scheduling remain absent. The native phase 1 NAS route remains healthy with its previously published aliases

The accounting correction passes live QA, 47 focused logging tests and 27 spend tests. The final `make check` passes, including generated dashboard API types. The managed proxy and PostgreSQL containers and their temporary network were stopped and removed without `-v`; `docker ps -a` confirms their absence. The PostgreSQL data directory and volumes remain, and both shared native proxies remain healthy

The full objective remains unfinished. The native SDK also rejects the complete OpenCode agent request with the same extra usage requirement, so subscription-only acceptance has not passed and the candidate is not promoted to Fedora or NAS. See the [implementation plan](../../docs/superpowers/plans/2026-10-01-anthropic-subscription.md) for the acceptance criteria

## Native SDK integration evidence

The isolated native broker passed Messages with all three models, Chat, Responses, both count routes and signed thinking with an external tool continuation. Five attributed native spend records match the deployed calculator. The dedicated native authorization has directory mode 0700 and credential mode 0600, and the native SDK refreshed an expired credential before exact token counting

The complete OpenCode 2.0.20 agent request fails before the first message event. Capturing the client's request and executing that exact body directly with Agent SDK 0.3.287 reproduces Anthropic HTTP 400 requiring extra usage. Its auxiliary title request succeeds, which explains why the earlier prompt-only probe did not establish full client compatibility. The native profile's OAuth usage endpoint returns HTTP 200 with extra usage disabled. No billing setting or application identity was changed to work around the rejection

The authenticated NAS Admin UI with the requested team filter displays the three canonical phase 1 aliases. The managed subscription aliases remain isolated until the complete client acceptance criteria pass

Native broker candidate 05, `sha256:0c61719c08c7fd4b782a8c536d16fa91f92dd9e91a7f26fedf2174fcd2d6b147`, completed real Codex 0.159.2 tool use and file creation with `workspace-write`. The first turn read `314159`, wrote `314160` and returned `CODEX_TOOL_OK`, with 209 reasoning tokens. A separate resume executed `cat proof-codex.txt`, read `314160` and returned `CODEX_RESUME_OK 314160`, with 297 reasoning tokens. This native evidence is separate from the earlier HTTP candidate

The broker accepts added caller tools through public MCP `tools/list_changed`, then waits for `tools/list` and the native SDK inventory before releasing pending results. It preserves the same Query and rejects removed or modified existing definitions, foreign histories and changed account controls. The 16 broker tests, build and independent review pass; the added regression fails against the previous source. All six compiled broker files matched the reviewed runtime

The final `make check` passes after the caller replay, dynamic tool inventory and launcher corrections, including Python lint, test quality, dashboard lint budgets and generated API types. No lint or type budgets were changed

After these checks, Compose down without `-v` stopped and removed the native SDK, proxy and PostgreSQL containers and their project network. `docker ps -a` and network listing confirm their absence. PostgreSQL data and dedicated credentials remain intact. Both shared proxies remain healthy on their previous images; the native candidate was not promoted
