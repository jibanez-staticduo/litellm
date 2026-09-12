# Portable Codex collaboration

The opt-in portable collaboration callback lets official Codex clients deliver plaintext assignments to models behind Responses-to-Chat-Completions bridges. It rewrites the reserved collaboration tool namespace upstream and restores official Codex function calls downstream, including the explicit plaintext delivery marker

Enable it only for the model aliases used by the parent and children:

```yaml
litellm_settings:
  callbacks:
    - litellm.proxy.hooks.portable_codex_agents.portable_codex_agents
```

Set `PORTABLE_CODEX_MODELS` to a comma-separated list of those aliases. The callback uses existing `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, and `REDIS_PASSWORD` environment variables. `PORTABLE_CODEX_REDIS_URL` optionally overrides that connection, including TLS or a separate Redis database

Set `PORTABLE_CODEX_NATIVE_MODELS` to the enabled aliases whose backend natively understands encrypted Codex Responses history. Existing tasks on these aliases retain their original transport when their first observed request contains encrypted or unconfirmed collaboration history, or an existing compaction checkpoint. Fresh tasks use plaintext collaboration. The callback records the chosen mode atomically per authenticated identity and stable `client_metadata.thread_id`; a legacy task does not automatically upgrade, and a known portable task does not downgrade when an individual replay proof is missing. External model aliases must not be included in this native allowlist

The parent must also opt in: modifying only the child's alias cannot recover an assignment already encrypted by its parent. All new portable tasks use plaintext assignments, including assignments to OpenAI-backed children. Other aliases, ordinary Responses requests without collaboration, and Chat Completions requests keep their existing transport. Start a fresh Codex task to use portable delegation; earlier encrypted assignments cannot be decrypted by this callback

Codex can omit the plaintext marker when replaying function calls. The adapter therefore records a SHA-256 fingerprint scoped to the authenticated key and team, function name, call ID, and exact arguments before returning a completed call. Redis stores only the fingerprint and a constant value, never the arguments. Entries use the `litellm:portable_codex_agents:v1:` prefix and have no expiry. The callback keeps original call IDs and uses no process-local proof cache

Redis availability is required for completed collaboration calls and for markerless replay. A Redis failure returns an explicit error. For a task with a recorded portable mode, missing proof requires a fresh task; the callback never assumes that missing metadata means plaintext. Persistence guarantees are those of the configured Redis instance: RDB snapshots alone can lose newer entries after a Redis crash. Moving a task between independent NAS and Fedora Redis instances is unsupported. Entries accumulate until explicitly cleaned; removing them invalidates markerless replay for the corresponding history

Thread modes use a separate `litellm:portable_codex_agents:mode:v1:` prefix without expiry. If Redis loses both a task's mode and its replay proofs, native aliases cannot distinguish that previously portable task from legacy history and may classify it as legacy on the next request. Recovery after Redis data loss is unsupported: start a fresh task. The no-downgrade guarantee applies while the recorded thread mode remains available

This callback supports full-history `POST /responses` requests, streaming and non-streaming. `previous_response_id` continuation is rejected on portable collaboration requests because it does not supply the complete tool provenance needed by this adapter. Plaintext `agent_message` input is represented as a user message with its author and recipient retained. Native encrypted reasoning items are not decrypted or relabeled

Disable the callback or remove an alias from `PORTABLE_CODEX_MODELS` to stop adapting new requests. Existing tasks using portable history should finish before disabling the feature
