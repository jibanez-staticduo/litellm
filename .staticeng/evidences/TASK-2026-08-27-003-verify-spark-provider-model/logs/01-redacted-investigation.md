# Redacted Investigation Record

## Versions And Catalog

- Installed Codex: `codex-cli 0.149.1`
- Upstream-derived cache record: `gpt-5.3-codex-spark`, visible, text-only, `supported_in_api=false`, `use_responses_lite=false`, default effort `high`, efforts `low/medium/high/xhigh`
- Official documentation: exact identifier `gpt-5.3-codex-spark`; ChatGPT Pro-only research preview; Codex CLI/IDE/desktop supported; API access unavailable
- Local custom catalog: same slug but `supported_in_api=true`, `use_responses_lite=true`, image input, and unrelated modern-model metadata

## Provider And Route Mapping

- LiteLLM catalog key: `chatgpt/gpt-5.3-codex-spark`
- LiteLLM provider: `chatgpt`
- Upstream endpoint: ChatGPT Codex Responses backend
- Upstream model after provider prefix removal: `gpt-5.3-codex-spark`
- NAS public route and two qualified profile deployments remained registered; Fedora had no Spark deployment

## Classified Provider Errors

- Earlier request: HTTP 400, invalid `all_turns`; upstream advertised `auto` and `current_turn`
- Corrected Codex-client request: HTTP 400, `invalid_request_error`, `param=model`, `code=unsupported_value`; model unsupported when the internal Codex Responses Lite header is present
- Direct standard-backend request in this task: HTTP 400; body not retained, no router fallback, no profile identity retained

## Safety

- Request count to an authenticated upstream profile: one
- Runtime/config/account mutations: zero
- Retained credentials, authorization headers, profile identities, prompts, or responses: zero
