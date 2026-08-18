---
id: TASK-2026-08-18-008-find-stream-must-be-true-fix
complexity: standard
track: investigation
slice: logic
status: done
scr: null
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-008 - Find Stream Must Be True Fix

## Objective
Identify the exact prior LiteLLM change and Fedora deployment action that resolved Codex failures with `ChatgptException: Stream must be set to true`, including source commit, files, tests, image/digest, and whether the current NAS/Fedora runtimes contain it.

## Classification
- **complexity:** standard
- **track:** investigation
- **slice:** logic

## Safety
- Read-only investigation only; do not change repository, NAS, Fedora, images, tags, database, or routing.
- Never expose credentials, prompts, response bodies, or authorization data.

## Acceptance Criteria
- [ ] AC-1: Locate the original session/task/evidence and summarize the root cause.
- [ ] AC-2: Identify exact commit(s), source file/function, regression tests, and behavioral fix.
- [ ] AC-3: Identify the Fedora image/tag/digest and deployment/verification evidence that removed the error.
- [ ] AC-4: Compare current NAS and Fedora runtime versions/digests/source labels and establish whether each contains the fix.
- [ ] AC-5: Recommend the minimum safe action if the error is currently reproducible on NAS or Fedora.

## Handoff
[Agent Message] From: product_manager To: explorer

Trace the exact historical fix using archived sessions, StaticEng tasks/evidence, Git history, and read-only runtime inspection. Focus on native `/v1/responses`, `extra_body`, and stream-override behavior. Return a signed shared-contract handback with precise non-secret references.

# Post Implementation Task Updates

## Explorer: Post Investigation Expectations
- AC-1 through AC-5 passed through archived-session, source, evidence, Git, and runtime inspection.
- Root cause: native Responses handlers merge `extra_body` after ChatGPT forces `stream=true`, allowing `stream=false` to overwrite the provider requirement.
- The historical fix was built but never committed; current NAS contains it, while current Fedora 1.98.0 and Git do not.
- No runtime mutation or live inference was performed.
- No product documentation update is required.
