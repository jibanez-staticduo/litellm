---
id: TASK-2026-09-01-006-check-upstream-restrictedpython
complexity: tiny
track: investigation
slice: qa
status: done
scr: null
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: Check upstream RestrictedPython vulnerability

## Objective

Determine whether current upstream LiteLLM `main` resolves RestrictedPython 8.1 and is affected by GHSA-ffg3-p8fm-mjx2.

## Acceptance Criteria

- [ ] AC-1: Inspect current upstream `main` dependency declarations and lock resolution without mutating the worktree.
- [ ] AC-2: Verify the advisory affected/fixed version range from an authoritative source.
- [ ] AC-3: State affected/not affected with commit/date evidence and any lock-vs-declaration nuance.

## Handoff

[Agent Message] From: product_manager To: explorer

Research only. Inspect the actual upstream LiteLLM repository `main` remotely, not the local dirty branch, and authoritative GHSA-ffg3-p8fm-mjx2 data. Do not fetch into or mutate the worktree. Return concise exact evidence: upstream commit, dependency declaration, lock resolution, affected/fixed range, conclusion. Update this task with signed handoff.

## Result

- AC-1: PASS. Upstream `main` at `10631eb834c7802aa61611e807474170b8a4d425` declares `RestrictedPython>=8.5,<9.0` and locks 8.5
- AC-2: PASS. GitHub's reviewed advisory marks `<=8.2` vulnerable and 8.3 first patched
- AC-3: PASS. Current upstream main is not affected; remediation entered upstream in `f1bebb6fbd5ab67a569aca616f62cd5604d768a1`

[Agent Message] From: explorer To: product_manager

PASS. Current upstream LiteLLM main is not affected. Both its proxy declaration and checked-in lock resolve above the patched threshold; the local candidate's 8.1 comes from this fork's older dependency state.
