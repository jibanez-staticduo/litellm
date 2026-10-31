# Portable Codex collaboration

The portable collaboration callback lets official Codex clients deliver plaintext assignments to models behind Responses-to-Chat-Completions bridges. It rewrites the reserved collaboration tool namespace upstream and restores official Codex function calls downstream, including the explicit plaintext delivery marker.

Enable the callback for Responses requests containing collaboration tools or history.

```yaml
litellm_settings:
  callbacks:
    - litellm.proxy.hooks.portable_codex_agents.portable_codex_agents
```

Collaboration detection applies to every model alias, including `local-codex` and aliases added later. `PORTABLE_CODEX_MODELS` remains accepted for configuration compatibility and no longer limits adaptation. The callback uses existing `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, and `REDIS_PASSWORD` environment variables. `PORTABLE_CODEX_REDIS_URL` optionally overrides that connection, including TLS or a separate Redis database.

Set `PORTABLE_CODEX_NATIVE_MODELS` to the aliases whose backend natively understands encrypted Codex Responses history. Existing tasks on these aliases retain encrypted collaboration history and compaction checkpoints while advertising portable tools for new calls. Fresh tasks use plaintext collaboration. The callback records the chosen mode atomically per authenticated identity and stable `client_metadata.thread_id`. A legacy task keeps its native backend requirement. External model aliases must not be included in this native allowlist.

New collaboration calls use plaintext assignments, including calls from existing native tasks and assignments to OpenAI-backed children. Existing native tasks can create external-model children with `fork_turns="none"` and an explicit plaintext assignment. Their encrypted parent history remains on the native backend. Inheriting that history into an external-model child is unsupported. Ordinary Responses requests without collaboration and Chat Completions requests keep their existing transport. Earlier encrypted assignments cannot be decrypted by this callback.

Codex can omit the plaintext marker when replaying function calls. Calls to `spawn_agent`, `send_message`, and `followup_task` are accepted without a Redis replay proof when their arguments are a JSON object containing a string `message`. This allows an existing task to switch between external and native aliases while retaining plaintext calls and their results. Invalid argument structures are rejected. An explicit encryption marker is never interpreted as plaintext. Markerless opaque arguments remain legacy history and are preserved only on native backends.

The adapter still records a SHA-256 fingerprint scoped to the authenticated key and team, function name, call ID, and exact arguments before returning a completed call. Redis stores only the fingerprint and a constant value, never the arguments. Entries use the `litellm:portable_codex_agents:v1:` prefix and have no expiry. These proofs remain useful for distinguishing other portable control calls in mixed legacy history. The callback keeps original call IDs and uses no process-local proof cache.

Redis availability is required for thread mode selection and completed collaboration calls. A Redis failure returns an explicit error. Thread modes use a separate `litellm:portable_codex_agents:mode:v1:` prefix without expiry. Valid plaintext message calls remain replayable when their fingerprint is missing, including when moving between independent NAS and Fedora Redis instances. Existing legacy mode restrictions and opaque history still require a native backend. This callback does not delete or migrate Redis records or task history.

This callback supports full-history `POST /responses` requests, streaming and non-streaming. `previous_response_id` continuation is rejected on portable collaboration requests because it does not supply the complete tool provenance needed by this adapter. Plaintext `agent_message` input is represented as a user message with its author and recipient retained. Native encrypted reasoning items are not decrypted or relabeled.

Disable the callback to stop adapting new requests. Existing tasks using portable history should finish before disabling the feature.
