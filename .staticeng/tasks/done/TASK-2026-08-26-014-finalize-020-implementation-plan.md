---
id: TASK-2026-08-26-014-finalize-020-implementation-plan
complexity: complex
track: spec
slice: foundation
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-014 - Finalize 0.2.0 Implementation Plan

## Objective
Produce the execution-ready plan for plugin 0.2.0, NAS shared-config cleanup, Codex alignment, and safe route retirements using the approved decisions.

## Acceptance Criteria
- [x] AC-1: Incorporate official defaults, user-last override precedence, Codex wire-valid subsets, and NAS defend route retirement.
- [x] AC-2: Decompose sequential atomic tasks with complexity/track/slice, ownership, dependencies, files/APIs, ACs, evidence, and rollback.
- [x] AC-3: Include release/tag/trusted-publish gates and unversioned shared plugin reference with stale-cache/version verification.
- [x] AC-4: Include NAS-only atomic config edit and Syncthing convergence verification without peer edits.
- [x] AC-5: Include Fedora-first normal GPT-5.3 retirement, NAS normal GPT-5.3 and defend retirement, dependency checks, and Spark preservation.
- [x] AC-6: Include full OpenCode/Codex matrix QA and explicit stop conditions.

## Expected Evidence
- Final plan written to `.staticeng/docs/plans/client-model-contracts-020-plan.md`.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

- AC-1: PASS. The plan incorporates the approved defaults, explicit user-last precedence, Codex 0.147 subsets, normal GPT-5.3 retirement, NAS defend retirement, and Spark separation
- AC-2: PASS. Six sequential tasks define classification, owner, dependencies, boundaries, files/APIs, numbered ACs, evidence, stop gates, and rollback
- AC-3: PASS. Release gates cover clean CI, `v0.2.0`, GitHub OIDC trusted publishing, npm provenance, unversioned resolution, scoped cache invalidation, and fresh-process version proof
- AC-4: PASS. The migration has one NAS writer, protected atomic edit, peer status/hash convergence, and no peer edits
- AC-5: PASS. Registry execution is Fedora-first and fail-closed, retires NAS normal GPT-5.3 and defend only after Fedora passes, and verifies Spark before and after each mutation
- AC-6: PASS. OpenCode and Codex have client-specific full-matrix verification and explicit global and task-local stop conditions

## Technical Architect Review Note

The plan is execution-ready after PMA creates the proposed tasks. The approved SCR was corrected in place to reflect the latest explicit user decision to retain the unversioned plugin reference, the GPT-5.6 Sol `medium` default, and Codex's wire-valid DeepSeek/Qwen limitations. No implementation, host configuration, package, cache, process, registry, or runtime state was changed

Documentation closure: `.staticeng/docs/plans/client-model-contracts-020-plan.md` is the execution source. Plugin steady-state architecture and README updates are assigned to Task 1

Validation: `staticeng_validate` was run and failed only on pre-existing repository-wide missing CodeMaps outside this planning task. Mandatory `staticeng_repair` dry-run and apply were run; repair reported no safe deterministic fix and left the module-boundary decisions unresolved. PMA must track that repository-level blocker separately; this task added no source or CodeMap structure
