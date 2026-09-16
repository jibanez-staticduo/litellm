# hosted_vllm_codex

This fork provides `hosted_vllm_codex` for clients that display Responses API reasoning summaries. It inherits the ordinary `hosted_vllm` request transformations and transport. The normal provider does not generate summaries

Use separate aliases pointing to the same backend:

```yaml
model_list:
  - model_name: qwen3.8-flash-next
    litellm_params:
      model: hosted_vllm/qwen3.8-flash-next
      api_base: http://your-vllm:8000/v1
      forward_reasoning_content: true
  - model_name: qwen3.8-flash-next-codex
    litellm_params:
      model: hosted_vllm_codex/qwen3.8-flash-next
      api_base: http://your-vllm:8000/v1
      forward_reasoning_content: true
```

An explicit Responses `reasoning.summary` value of `auto`, `concise`, or `detailed` enables summarization. Omitted summaries, `none`, ordinary Chat Completions and the normal provider do not start auxiliary inference. In Codex, the model catalog must enable `supports_reasoning_summary_parameter` and the effective reasoning-summary setting must not be `none`

The primary reasoning stays in the reasoning item's `content`. When that reasoning ends, a separate streaming request receives only the reasoning text and a summarization instruction. It uses the same backend/model, disables thinking through `chat_template_kwargs.enable_thinking=false`, and limits generated output to 500 tokens. It uses the ordinary provider internally to avoid recursion

Both upstream streams are consumed concurrently. Delivery of primary content and tool events after reasoning is temporarily buffered so Codex receives the summary while the original reasoning item is still active. Summary events use that item's ID and output index, then its completion is delivered before the buffered primary events in their original order. Delivery can therefore delay tool execution while the summary finishes or reaches its 30-second deadline. The buffer releases at 128 events or 1 MiB of serialized event data; reaching either limit cancels only the auxiliary summary and releases all primary events, including the event that triggered the limit. An individual event can exceed the byte limit temporarily. Summary capacity is limited to eight concurrent calls per process; when unavailable or failing, the primary response still completes. This does not eliminate final-response latency or GPU contention

The summary is additional display content, never a replacement for the original reasoning used for history replay. Main response usage stays unchanged so auxiliary input is not mistaken for conversation context. The auxiliary call has its own usage and restricted caller-attribution metadata, with additional usage available in internal `reasoning_summary_usage` metadata

Keep OpenCode and other Chat Completions consumers on the normal alias. Clients that display both raw reasoning and summaries can otherwise show duplicate information. This feature does not provide encrypted reasoning or change the backend tokenizer
