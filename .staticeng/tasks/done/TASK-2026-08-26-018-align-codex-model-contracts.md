---
id: TASK-2026-08-26-018-align-codex-model-contracts
complexity: complex
track: implementation
slice: core
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-26-018 - Align Codex Model Contracts

## Objective
Align the NAS local Codex custom model catalog and active configuration with the approved GPT, DeepSeek, and Qwen wire-valid reasoning matrix.

## Acceptance Criteria
- [x] T4-AC-1: Fresh protected backups/baseline; retained rows cover approved families, normal GPT-5.3 absent, Spark preserved.
- [x] T4-AC-2: GPT rows have exact modes/defaults; DeepSeek `none/low/high/max`; Qwen `low/medium/xhigh`; no `ultra`.
- [x] T4-AC-3: Active config retains the custom catalog/Responses provider and valid DeepSeek `high`; unrelated config is byte-identical.
- [x] T4-AC-4: JSON/TOML and a fresh isolated Codex 0.149.1 app-server/model list pass; generated cache is not hand-edited and fresh process identity is recorded.
- [x] T4-AC-5: Isolated redacted Responses captures prove each exposed mode for every distinct row, including GPT none/max, DeepSeek none, Qwen xhigh.
- [x] T4-AC-6: No DeepSeek visible off, no Qwen Off, no stale global effort on row switching, no binary patch.
- [x] T4-AC-7: Complete evidence, permissions, checksums, rollback, and no hand-edit of generated cache.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-018-align-codex-model-contracts/` with `SUMMARY.md` and redacted logs.

## Reopen History

### Reopen 1 - 2026-08-27
- Initial candidate was rolled back because validation incorrectly treated historical Codex 0.147 as authoritative; current config contains a valid 0.149.1-only `[execution]` section.
- Authoritative runtime is installed Codex 0.149.1. Preserve current active DeepSeek `high` because it is valid; do not force GPT-5.6 Sol active.
- Reapply only the approved custom-catalog matrix, validate with fresh 0.149.1 processes, and preserve all unrelated config sections byte/semantically unchanged.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Status: PASS on Reopen 1 under authoritative Codex 0.149.1
- Fresh owner-only Reopen 1 backups were created for config, custom catalog, and generated cache before mutation
- Only the custom catalog reasoning lists/defaults changed; row order and every unrelated row field remain unchanged
- `config.toml` remains byte-identical, including active DeepSeek `high`, Responses provider, catalog path, `[execution]`, and unrelated sections
- Fresh isolated Codex 0.149.1 app-server initialization and `model/list` returned the exact nine-row selector matrix
- Forty-five catalog row/mode captures and five explicit row-switch captures sent exact loopback-only Responses efforts with no production inference
- No historical process was killed, no binary was patched, and production `models_cache.json` hash/mtime remained unchanged
- Product documentation is not required; operational evidence records the retained steady state and rollback assets
