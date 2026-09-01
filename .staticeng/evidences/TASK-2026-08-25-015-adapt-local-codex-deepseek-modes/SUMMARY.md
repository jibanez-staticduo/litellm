# Evidence Summary: TASK-2026-08-25-015

Codex CLI `0.147.0` now advertises and emits exactly `off`, `low`, `high`, and `max` for `deepseek-v4-flash-fp8-mtp`. The target catalog default and active global effort are `max`. No production request was sent

## Acceptance Criteria Coverage

- AC-1: PASS. Owner-only backups, SHA-256 checksums, ownership/modes, catalog provenance, and exact rollback are recorded in `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/01-baseline-backup-rollback.md`
- AC-2: PASS. The local catalog is the authoritative manually maintained file selected by `model_catalog_json`; only the exact target row changed. It now has default `max` and ordered efforts `off`, `low`, `high`, `max`. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/02-catalog-config-scope.md`
- AC-3: PASS. Active `model_reasoning_effort` changed from `medium` to `max`; every other parsed config field is equal to backup. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/02-catalog-config-scope.md`
- AC-4: PASS. JSON parsing, Codex strict config parsing, `codex debug models`, and app-server `model/list` passed. The selector returns exactly the four approved efforts. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/03-parser-selector.md`
- AC-5: PASS. Four isolated loopback Responses captures contain unchanged efforts `off`, `low`, `high`, and `max`. Selector output excludes `medium` and `xhigh`. Captures store no prompt, body, header, or credential value. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/04-sanitized-wire-capture.md`
- AC-6: PASS. Unrelated catalog rows, row order, provider endpoint/config fields, credential helper reference, ownership, and modes remain unchanged. No LiteLLM, OpenCode, plugin, service, or production endpoint was touched. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/02-catalog-config-scope.md`
- AC-7: PASS. Backup readability and hashes were verified, rollback restores the catalog/config pair, and this packet provides complete sanitized evidence. `staticeng_validate` remains blocked by pre-existing repository-wide missing CodeMaps unrelated to this local configuration task. See `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/05-validation.md`

## Changed Owner Files

- `/home/staticduo/.local/share/codex-nas/codex-litellm-models.json`: target row only
- `/home/staticduo/.codex/config.toml`: `model_reasoning_effort` only

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. The approved SCR and steady-state reasoning contract already define this behavior; this task applies that contract to owner-local Codex configuration

## Rollback

Run the commands in `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/logs/01-baseline-backup-rollback.md` as user `staticduo`, then rerun `python3 -m json.tool`, `codex debug models`, and app-server `model/list`. No service restart is required for new Codex processes
