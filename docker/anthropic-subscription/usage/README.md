# Claude usage

`claude_usage` queries `GET https://api.anthropic.com/api/oauth/usage` with the native access token in each profile's `.credentials.json`. It does not perform inference, refresh tokens, enable extra usage or write credentials

Run `./claude_usage` for the human view or `./claude_usage --json` for schema version 1. Profiles default to `staticduo` and `defend1` under `~/.claude-homes`. Select profiles with repeated `--profile NAME` or `--account NAME`. Override the root with `--profiles-dir PATH` or `CLAUDE_USAGE_PROFILES_DIR`. Human reset times default to `Europe/Brussels`; `--timezone` changes the display only

For installation, copy this directory to the chosen deployment path and symlink its `claude_usage` executable into `~/.local/bin`. The launcher resolves symlinks before locating `collector.py`

The JSON object contains `schema_version`, `generated_at` and `profiles`. Each profile contains `name`, `plan`, `status`, `five_hour`, `weekly`, `scoped_windows`, `extra_usage` and `error`. Quota windows contain `used_percent`, UTC `reset_at` and `limit_window_seconds`. A missing window remains `null`; zero means the endpoint explicitly reports zero utilization. Unknown scoped windows are not inferred from unrelated fields

Extra usage is separate from subscription quota. `enabled`, `monthly_limit`, `used_credits` and `utilization` retain nullable upstream values. Monetary numbers use upstream units; they are not converted to currency amounts or tokens

Errors contain a fixed `code` and optional `http_status`, without response bodies or exception details. Expired or rejected access requires native authentication via `claude_NAME auth login --claudeai`. The collector has no independent refresh owner

This endpoint is hosted by Anthropic but has no published stable API contract. Its response and headers were checked against the live endpoint on 2026-10-04. Community endpoint documentation: [usage endpoint discussion](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor/issues/202). The public [API overview](https://platform.claude.com/docs/en/api/overview) does not document this subscription endpoint. Avoid frequent polling; a 429 is a usage-query rate limit and does not prove inference quota exhaustion

Run the focused tests with `python3 -m unittest discover -s docker/anthropic-subscription/usage -v` from the repository root
