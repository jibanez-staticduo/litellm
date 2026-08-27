---
id: TASK-2026-08-26-012-discover-client-contract-migration
complexity: complex
track: investigation
slice: foundation
status: done

# Post Implementation Task Updates

## Explorer: Post Implementation Expectations
- Read-only inventory complete; no files, routes, services, or clients changed.
- Exact route IDs, override blocks, rollback constraints, and plugin boundaries are recorded in the signed handoff.
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-012 - Discover Client Contract Migration

## Objective
Map current plugin, OpenCode, Codex, and both LiteLLM registry state needed to plan the 0.2.0 built-in contract migration without implementation.

## Acceptance Criteria
- [ ] AC-1: Inventory every current GPT, DeepSeek V4, and Qwen3.8 alias in NAS/Fedora, OpenCode resolved config/overrides, and Codex catalog/config.
- [ ] AC-2: Identify exact plugin 0.1.9 contract logic, override merge semantics, release workflow, and suitable internal-contract module boundary.
- [ ] AC-3: Identify every noisy known-model override removable from NAS `opencode.json` and every unrelated block that must remain unchanged.
- [ ] AC-4: Identify obsolete GPT-5.3 Codex normal routes/dependencies on both proxies and clients; distinguish Spark.
- [ ] AC-5: Return exact files/APIs, dirty-worktree constraints, Syncthing considerations, versions, and rollback sources.

## Expected Evidence
- Signed read-only handoff with secrets/account identities redacted.
