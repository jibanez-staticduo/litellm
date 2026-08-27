# Reopen 1 Catalog and App-Server Validation

Atomic post-write catalog SHA-256: `2712f1073ce71165a0c546410e485eadb75f3a502589fd217b7dc58a60d7384b`

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

- JSON and TOML syntax: PASS
- Catalog row order and unrelated-field equality: PASS
- Config byte equality with Reopen 1 backup: PASS, SHA-256 `2e43a9c67960f16db1756d0b2df3a0350150add7d89765e9d7909ccd0c16c63e`
- Fresh isolated app-server identity: `task-018-r1-isolated/0.149.1`, task-created PID recorded during execution and terminated after response
- `initialize` plus `model/list`: PASS, nine exact rows
- Normal GPT-5.3 absent, Spark retained, DeepSeek no `off`, Qwen no Off, no `ultra`: PASS
- Production cache before/after hash and nanosecond mtime: identical
- Isolated app-server did not create an isolated `models_cache.json`; no cache was hand-created or edited
