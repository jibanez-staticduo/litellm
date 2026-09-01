# Catalog and Config Scope

Post-change SHA-256:

- Config: `9444734a2a137384bc4ae7890f6f144eb53d1d6fefa73375f1d09b336e831504`
- Catalog: `0376763ce478acf9af94d3c36a58e91370140abcf62155f3045d335db4378266`

Semantic comparisons against protected backups:

```text
changed_rows ['deepseek-v4-flash-fp8-mtp']
catalog_row_order_equal true
target_default max
target_efforts [off, low, high, max]
config_changed_key model_reasoning_effort: medium -> max
config_other_fields_equal true
```

No other catalog row changed. Provider name, Responses wire API, base URL, credential helper reference, retry values, project trust settings, and all other config fields compare equal. No credential content was read or captured

Active file ownership/modes after change:

```text
/home/staticduo/.codex/config.toml mode=777 owner=staticduo group=admin
/home/staticduo/.local/share/codex-nas/codex-litellm-models.json mode=600 owner=staticduo group=admin
```
