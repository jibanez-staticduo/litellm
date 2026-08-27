# Reopen 1 Preflight and Backups

- Authoritative runtime: `codex-cli 0.149.1`
- Active model/effort: `deepseek-v4-flash-fp8-mtp` / `high`
- Provider/catalog/wire: `nas_litellm`, owner-local custom catalog, Responses API
- Historical 0.147 processes were inventoried but not treated as gates and not terminated
- Reopen 1 production cache baseline: SHA-256 `62d53fde89be8b1c0dbf74a95a0829e7f3d8d08b037e38dea5a7947d8dd868a2`

Fresh backups, timestamp `20260827T054500Z`:

```text
/home/staticduo/.codex/config.toml.backup-TASK-018-R1-20260827T054500Z
mode=0600 sha256=2e43a9c67960f16db1756d0b2df3a0350150add7d89765e9d7909ccd0c16c63e
/home/staticduo/.local/share/codex-nas/codex-litellm-models.json.backup-TASK-018-R1-20260827T054500Z
mode=0600 sha256=0376763ce478acf9af94d3c36a58e91370140abcf62155f3045d335db4378266
/home/staticduo/.codex/models_cache.json.backup-TASK-018-R1-20260827T054500Z
mode=0600 sha256=62d53fde89be8b1c0dbf74a95a0829e7f3d8d08b037e38dea5a7947d8dd868a2
```

Rollback restores only config/catalog from these exact backups through protected temporary files plus atomic rename. Generated cache is restored only if future verification proves Codex itself changed it; this run left it byte-for-byte and timestamp-identical
