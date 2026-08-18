---
id: SCR-2026-08-18-002-stream-safe-198-both-hosts
status: approved
requested_by: user
approved_by: user
date: 2026-08-18
---

# SCR: Stream-Safe LiteLLM 1.98.0 on NAS and Fedora

## Requested Behavior
- Persist the ChatGPT native Responses stream guard in current LiteLLM `main` so `extra_body.stream=false` cannot override provider-required `stream=true`.
- Persist the ChatGPT fake-stream bypass so ChatGPT Responses uses native streaming even when capability metadata is incomplete.
- Build one immutable LiteLLM 1.98.0 image from current `main` containing both fixes.
- Deploy the same verified image to NAS and Fedora, preserving each host's models, routing, credentials, databases, and account topology.

## Acceptance Intent
- Codex `/v1/responses` requests must not emit `Stream must be set to true` on either host.
- NAS retains default `chatgpt` as primary for the eight public GPT aliases, with account2/account3 retained as fallbacks.
- Fedora retains its current two-account topology and unrelated services/configuration.
- Both hosts remain healthy and have tested rollback references.

## Approval
Approved directly by the user on 2026-08-18.
