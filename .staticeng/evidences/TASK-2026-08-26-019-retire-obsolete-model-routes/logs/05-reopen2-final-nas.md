# Reopen 2 Final NAS Retirement

## Preflight And Rollback

- Fresh inventory: seven target deployments, the same UUID/upstream projection as Reopen 1 rollback
- Access: every target exposed through the same two teams; direct access and blocked state were captured in the protected snapshot
- Dependencies: one normal public fallback, one Spark public fallback, and five defend fallback mappings; no target default, model-group alias, or routing group
- Backup: PostgreSQL custom format, 1,897,377,657 bytes, 415-entry successful restore listing, mode `0600`
- Checksum: passed `sha256sum -c`; exact value remains in the protected host-local `.sha256` file
- Exact credential-complete recreation payloads for all seven UUIDs remain in the mode `0700` host-local Reopen 2 directory

## Mutation

- Authenticated host-local `/config/update` removed target fallback sources and target destinations while preserving 12 unrelated non-empty mappings
- Authenticated host-local `/model/delete` returned HTTP 200 for all seven exact deployment IDs
- No direct database write, source edit, configuration-file edit, or client-catalog edit occurred

## Verification

- Post-restart readiness: HTTP 200, DB connected, container healthy
- Raw database target count: zero
- `/model/info`, `/model_group/info`, `/router/settings`, and `/v1/models`: zero normal, Spark, or defend references
- Unrelated deployment identity sets: zero missing, zero added
- Unrelated access memberships: zero changed after normalizing set order
- Scoped mutation logs: no model-delete, fallback, or config-update failure match
- Unavailable requests: normal public/qualified, Spark public/qualified, and defend aliases all returned HTTP 400 with no deployment identity header
- No prompt or output was retained; probes used only the bounded one-character status payload with `store=false` and zero client retries

## Client And Dual-Host State

- OpenCode cache package: `@staticeng/opencode-litellm` version `0.2.2`
- Fresh `opencode models LiteLLM`: zero GPT-5.3 aliases
- Fresh Codex: `codex-cli 0.149.1`, eight `model/list` rows, zero GPT-5.3 aliases
- Fedora final check: readiness HTTP 200, zero GPT-5.3 references in model and router projections
- Final state: both LiteLLM hosts and both current client discovery surfaces omit normal GPT-5.3 and Spark; NAS additionally omits defend
