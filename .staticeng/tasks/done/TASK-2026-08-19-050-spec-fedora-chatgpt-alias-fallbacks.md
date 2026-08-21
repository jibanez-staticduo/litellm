---
id: TASK-2026-08-19-050-spec-fedora-chatgpt-alias-fallbacks
complexity: standard
track: spec
slice: logic
status: done
scr: SCR-2026-08-19-001-fedora-chatgpt-alias-fallbacks
parent: TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-050 - Specify Fedora ChatGPT alias fallbacks

## Objective
Anchor the user-approved Fedora routing policy so every unqualified ChatGPT alias uses account1 first and account2 as fallback on account1 failure, including rate limit.

## Acceptance Criteria
- [x] AC-1: Create `SCR-2026-08-19-001-fedora-chatgpt-alias-fallbacks` with the approved behavior and explicit scope.
- [x] AC-2: Specify that qualified account1/account2 routes remain explicit and unchanged.
- [x] AC-3: Cover all six discovered unqualified aliases and require exact live readback after repair.
- [x] AC-4: Define bounded verification proving account1 rate limit advances to account2 without changing credentials, retries, cooldowns, deployments, or source.
- [x] AC-5: Create an atomic implementation task with numbered acceptance criteria and evidence requirements.

## Handoff
[Agent Message] From: product_manager To: business_analyst

Use the user's explicit approval in this conversation as product-owner approval. Base the SCR on TASK-049 evidence. Keep the repair configuration-only and require all six public aliases to implement account1 primary plus account2 fallback consistently. Do not implement or commit.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary
- Created approved SCR `SCR-2026-08-19-001-fedora-chatgpt-alias-fallbacks` from the user's explicit product-owner decision
- Fixed scope to the six unqualified Fedora aliases established by TASK-049 evidence
- Created one atomic implementation task, `TASK-2026-08-19-051-implement-fedora-chatgpt-alias-fallbacks`

### Acceptance Criteria Coverage
- AC-1: PASS. The SCR records approved behavior, scope, exclusions, acceptance intent, basis, and approval source
- AC-2: PASS. The SCR and implementation task preserve qualified account1/account2 routes as explicit identities
- AC-3: PASS. Both artifacts name all six aliases and require exact persistent/live readback, including the missing Luna rule
- AC-4: PASS. The implementation task requires bounded stateless no-retry rate-limit traversal evidence without credential, deployment, retry, cooldown, or source mutation
- AC-5: PASS. TASK-051 contains complete frontmatter, numbered ACs, evidence requirements, safety, rollback, and a signed PMA handoff

### Documentation Impact
- Added the approved SCR to the active SCR registry
- Updated task registries and archived this completed specification task
- No runtime, source, product overview, feature list, or steady-state behavior changed during specification

### Open Risks
- TASK-049 readback shows inconsistent public deployment profiles. TASK-051 therefore has a mandatory precondition to stop if fallback-only settings cannot guarantee account1-first ordering without violating the approved preservation constraints

### Recommended Next Step
- PMA should dispatch TASK-051 to a developer for preflight and configuration-only implementation
