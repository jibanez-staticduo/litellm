---
id: TASK-2026-08-26-013-specify-model-contract-catalog
complexity: complex
track: spec
slice: foundation
status: done

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations
- Product matrix completed and subsequently reconciled by PMA with explicit user decisions in the approved SCR.
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-013 - Specify Model Contract Catalog

## Objective
Define the product matrix and acceptance criteria for built-in GPT, DeepSeek V4, and Qwen3.8 contracts in plugin 0.2.0 and Codex.

## Acceptance Criteria
- [x] AC-1: Define exact visible modes, wire mappings, and defaults for every distinct model family/version and alias class.
- [x] AC-2: Define deprecation behavior for GPT-5.3 Codex normal versus Spark.
- [x] AC-3: Define precedence between built-in contracts, discovery metadata, and retained user overrides.
- [x] AC-4: Define what empty known-model overrides means in shared `opencode.json` and which unrelated customization remains.
- [x] AC-5: Produce numbered implementation/end-to-end acceptance criteria and explicit non-goals.

## Expected Evidence
- Signed product specification handoff with the shared output contract.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

- Expanded proposed SCR `SCR-2026-08-26-002-client-model-contracts-020` into the complete product contract and implementation gate for plugin 0.2.0
- Resolved override precedence as built-in contract over user override over discovery for protected reasoning fields, while retaining user-over-discovery behavior for unrelated metadata and all unknown models
- Defined that known models remain customizable only outside protected reasoning fields; conflicting protected fields are sanitized after merge so invalid levels cannot return
- Defined exact GPT, DeepSeek V4, and Qwen3.8 mode/default/wire matrices, alias classes, normal GPT-5.3 Codex retirement, clean shared configuration, Codex behavior, non-goals, and AC-1 through AC-14

## BA Review Note

The specification is complete and testable but remains proposal-state product behavior until the user approves the SCR. PMA must not authorize implementation before approval
