# Preflight and Protected Backups

- Active command version: `codex-cli 0.149.1`
- Retained target binary: `codex-cli 0.147.0`
- Process inventory found long-running 0.147 app-server/code-mode-host processes and separate 0.149 app-server proxy processes; no process was terminated
- Observed active model/effort: `deepseek-v4-flash-fp8-mtp` / `high`
- Custom provider/catalog: `nas_litellm` / owner-local custom catalog
- Wire API: `responses`
- Baseline custom catalog: nine rows; Spark present; normal GPT-5.3 absent
- Baseline generated-cache SHA-256: `62d53fde89be8b1c0dbf74a95a0829e7f3d8d08b037e38dea5a7947d8dd868a2`

Fresh backups, timestamp `20260827T054004Z`:

```text
/home/staticduo/.codex/config.toml.backup-TASK-018-20260827T054004Z
mode=0600 sha256=2e43a9c67960f16db1756d0b2df3a0350150add7d89765e9d7909ccd0c16c63e
/home/staticduo/.local/share/codex-nas/codex-litellm-models.json.backup-TASK-018-20260827T054004Z
mode=0600 sha256=0376763ce478acf9af94d3c36a58e91370140abcf62155f3045d335db4378266
/home/staticduo/.codex/models_cache.json.backup-TASK-018-20260827T054004Z
mode=0600 sha256=62d53fde89be8b1c0dbf74a95a0829e7f3d8d08b037e38dea5a7947d8dd868a2
```

No credential, endpoint authorization value, prompt, response content, or unredacted config is retained here
