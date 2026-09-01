# Baseline, Backup, and Rollback

- Codex version: `codex-cli 0.147.0`
- Active config: `/home/staticduo/.codex/config.toml`, owner `staticduo:admin`, mode preserved as `0777`
- Catalog: `/home/staticduo/.local/share/codex-nas/codex-litellm-models.json`, owner `staticduo:admin`, mode preserved as `0600`
- Config backup: `/home/staticduo/.codex/config.toml.backup-TASK-015-20260825T133046Z`, mode `0600`, SHA-256 `e4d735e94e213f46b6724eab00ab7492dd948c1e7bc4d135a7cb897757390274`
- Catalog backup: `/home/staticduo/.local/share/codex-nas/codex-litellm-models.json.backup-TASK-015-20260825T133046Z`, mode `0600`, SHA-256 `77c06994c3f89d66c1a4a0109a0e04b904e10b5d3bbf2999f466840b7ad9c4a4`
- Baseline target catalog default/options: `medium`; `low`, `medium`, `high`
- Baseline active effort: `medium`

The catalog path is directly configured by `model_catalog_json`. A bounded search of user-local scripts, systemd units, and Codex package files found no generator. Prior task `TASK-20260804-codex-catalog-add-local-models` also identifies this manually maintained file as the owner-local catalog. Codex's `models_cache.json` is generated runtime cache, not the configured source

Exact rollback, including original active modes:

```bash
install -m 777 /home/staticduo/.codex/config.toml.backup-TASK-015-20260825T133046Z /home/staticduo/.codex/config.toml
install -m 600 /home/staticduo/.local/share/codex-nas/codex-litellm-models.json.backup-TASK-015-20260825T133046Z /home/staticduo/.local/share/codex-nas/codex-litellm-models.json
python3 -m json.tool /home/staticduo/.local/share/codex-nas/codex-litellm-models.json >/dev/null
codex debug models >/dev/null
```

The protected backups parse and compare to the recorded baseline hashes. Restore both together because the baseline active `medium` setting requires the baseline catalog's `medium` option
