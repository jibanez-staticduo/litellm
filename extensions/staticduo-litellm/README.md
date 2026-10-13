# StaticDuo LiteLLM extension

Versioned in-process policies for the StaticDuo LiteLLM fork. The distribution
contains Portable Codex, pricing, provider, compression and LazyMCP modules.
Install `staticduo-litellm[proxy]` for callback and MCP integration dependencies;
the base wheel keeps catalog and protocol policies available without a proxy.
LiteLLM imports belong to `staticduo_litellm.compatibility`; policy modules can
be imported without installing LiteLLM. The extension does not depend on
LiteLLM, avoiding a circular package dependency.

The root uv workspace supplies `staticduo-litellm==0.1.0`. Production images
install non-editable wheels through `uv sync --frozen --no-editable`. Existing
callback configuration remains valid:

```yaml
litellm_settings:
  callbacks:
    - litellm.proxy.hooks.portable_codex_agents.portable_codex_agents
```

The exported callback is the concrete compatibility class so LiteLLM discovers
its request, success and streaming hooks. Redis replay proofs and thread mode
remain isolated by authenticated owner and stable Codex thread identity.

Build the standalone wheel with `uv build --package staticduo-litellm --wheel`.
