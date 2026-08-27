# Candidate Validation and Stop Condition

The candidate changed only each row's `default_reasoning_level` and `supported_reasoning_levels`, plus active config model and effort. All unrelated catalog fields and config lines compared equal

Codex 0.147 rendered this sanitized matrix:

```text
gpt-5.3-codex-spark default=high levels=none,low,medium,high,xhigh
gpt-5.4 default=none levels=none,low,medium,high,xhigh
gpt-5.4-mini default=none levels=none,low,medium,high,xhigh
gpt-5.5 default=medium levels=none,low,medium,high,xhigh
gpt-5.6-luna default=medium levels=none,low,medium,high,xhigh,max
gpt-5.6-sol default=medium levels=none,low,medium,high,xhigh,max
gpt-5.6-terra default=medium levels=none,low,medium,high,xhigh,max
deepseek-v4-flash-fp8-mtp default=max levels=none,low,high,max
qwen3.8-27b-refusal-dial default=xhigh levels=low,medium,xhigh
```

Checks before the stop:

```text
JSON parse: PASS
TOML syntax parse: PASS
Codex 0.147 debug-models catalog render: PASS, 9 rows
Normal GPT-5.3 absent: PASS
Spark preserved: PASS
No ultra: PASS
Generated cache hash/mtime unchanged by debug-models: PASS
Fresh strict Codex 0.147 app-server/config parse: FAIL
```

Sanitized failure:

```text
active config line 51: unknown configuration field `execution`
```

This unrelated active section predates and falls outside the approved mutation set. Under global stop conditions 3, 6, and 7, no attempt was made to remove it, patch Codex, hand-edit generated cache, run wire captures, or terminate unrelated sessions
