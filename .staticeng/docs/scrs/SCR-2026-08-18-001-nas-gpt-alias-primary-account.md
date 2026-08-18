---
id: SCR-2026-08-18-001-nas-gpt-alias-primary-account
status: approved
requested_by: user
approved_by: user
date: 2026-08-18
---

# SCR: NAS GPT Alias Primary Account

## Requested Behavior
For every NAS LiteLLM `gpt-*` alias backed by the ChatGPT Responses provider, the primary deployment must use the default `chatgpt` account rather than `account2` or `account3`.

## Scope
- NAS LiteLLM routing configuration/database only.
- Scope is the eight current ChatGPT Responses aliases from `gpt-5.3-codex` through `gpt-5.6-terra` identified in preflight.
- `gpt-4o-mini-tts` is explicitly excluded because it is an OpenAI speech route, not a ChatGPT-account alias.
- Preserve alias names, model inventory, credentials, and non-`gpt-*` routes.
- Existing account2/account3 deployments may remain available, but must not be primary for `gpt-*` aliases.
- Fedora is out of scope.

## Approval
Approved directly by the user on 2026-08-18.
