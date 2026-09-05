---
id: TASK-2026-09-05-001-repair-fedora-runtime
complexity: complex
track: implementation
slice: logic
status: active
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
---

# Repair Fedora LiteLLM runtime

## Scope and authorization

User directs live repair on Fedora without rollback, then promotion to NAS only after Fedora works. Security remediation and tooling refactors are out of scope. Fedora candidate was stopped after readiness timeout, 39 restarts and 29 GiB memory with unlimited effective cgroups. Preserve NAS and all data. One implementation owner only.

## Acceptance criteria

- AC-1: Determine actual Compose/recreation path and make candidate containment persistent through that path; verify actual 8 GiB/no-swap cgroups and restart policy after recreation. Do not merely leave an unused override file.
- AC-2: Establish request-correlated source of memory growth/restarts and deployment availability failures using bounded existing observability; distinguish cause from incidental rate-limit noise.
- AC-3: Apply minimal proven LiteLLM source or runtime configuration correction; add relevant regression tests if source changes. No harness refactor, no speculative retry increases.
- AC-4: Start candidate and verify readiness, real models/Responses, MCP/LazyMCP read-only tools and resource stability. No Fedora rollback. Stop only if necessary to protect host/data, retaining candidate selection.
- AC-5: Record exact changed files, source/image identity, verification and unresolved issues in `.staticeng/evidences/TASK-2026-09-05-001-repair-fedora-runtime/SUMMARY.md` and logs. Product docs updated if needed. No secrets in evidence.

## Handoff

[Agent Message] From: product_manager To: developer

Read parent task and latest logs/11-resume-containment-loss.md. Inspect current state first. You alone own implementation, including authorized Fedora configuration/service changes and minimal product code fixes. Investigate and fix, not just recommend. Use existing commands rather than building diagnostic frameworks. Do not touch NAS, rotate credentials, change global security policy, commit or push. Return runnable repair and concrete evidence for independent verification. Preserve unrelated worktree changes.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

AC-1 is verified: Fedora base docker-compose.yaml now persists restart=no, mem_limit=8g and memswap_limit=8g, verified through actual recreation and cgroups. Three subsequent bounded executions reproduced cgroup OOM without automatic restart. Candidate remains selected but exited, not repaired or release-qualified

AC-2/AC-3 remain partial. Existing debug endpoints showed bounded task counts before synchronous growth and event-loop starvation; a bounded native gdb sample found the main thread in dictionary insertion with repeated pydantic_core frames. Exact Python caller/request attribution is not yet proven. No speculative source fix was applied

AC-4 failed: initial readiness and model listing passed, real gpt-6-astra Responses returned 400, then runtime OOM. Full real-model/MCP verification and soak remain incomplete. AC-5 evidence is in `.staticeng/evidences/TASK-2026-09-05-001-repair-fedora-runtime/`. No commit/push or NAS deployment mutation occurred. Product documentation is not required because no product behavior was changed; evidence documents the operational containment correction

[Agent Message] From: developer To: product_manager

Persistent containment repaired; product blocker reproduced three times. Request Tech Lead help to identify the Python caller above repeated native pydantic_core allocation frames under the original task. Candidate is selected but safely exited with restart disabled and 8-GiB/no-swap limits. Do not promote to NAS or treat startup readiness as repair success. No new harness or speculative retry change was made

## Tech Lead: Post Implementation Expectations

Same-task escalation captured the exact Python allocating caller twice: ChatGPT Responses header validation serializes all GenericLiteLLMParams in `_normalize_litellm_params` while deriving a session ID. A second stack proves incoming routed chat through the Chat-to-Responses bridge, not a background task. A minimal local BaseModel attribute-projection patch and mapped regression tests are ready for review

AC-2 now has an exact allocating code path and bounded synthetic reproduction; the live graph producer and request ID remain unproven. AC-3 is locally implemented with 33 passing Responses tests and mutation-sensitive serializer-spy coverage, but not release-qualified. The broader suite has three auth-profile propagation failures reproduced with this patch removed. These require PMA routing before closure. AC-4 remains failed/incomplete: no corrected image was deployed or soaked

See evidence logs/02-tech-lead-python-caller.md and the updated SUMMARY. Product-facing behavior is unchanged; the CodeMap documents the no-recursive-serialization invariant. No new public feature documentation is required. Task remains active, Fedora stopped on the selected contained candidate, NAS untouched, no commit/push

## Reopen History

2026-09-05: Continued the active original task after three Developer failures, with PMA explicitly pausing Developer and assigning exclusive technical diagnosis to Tech Lead. Returned a local source correction and tests without claiming task closure or release success

2026-09-05: PMA paused Tech Lead and resumed exclusive Developer ownership. Preserved the no-serialization patch and repaired the three auth-profile propagation failures by restoring optional-key extraction. Focused suite: 115 passed, no skips. Full requested router/Responses folders: 964 passed, 15 failed, no skips. Six assertion failures and nine integration-environment failures remain blocking; no behavior/test weakening was performed

### Developer resume expectations

Pinned-toolchain make check remains blocked by two maintenance-test findings outside the implemented source fixes. Source Ruff, strict/type budgets and StaticEng validation passed. No corrected image exists and no new Fedora deployment/soak was attempted. The five-path review patch/hash and detailed failed results are in the evidence summary. No commit/push occurred

The broad router suite was not isolated: a real-provider speech test reached the inherited configured gateway. No NAS deployment/configuration/service change was made, but zero endpoint traffic cannot be claimed. PMA must provide or approve an isolated integration environment before those cases run again

[Agent Message] From: developer To: product_manager

Original three profile failures fixed, 115 focused tests pass. Qualification remains blocked by 15 broader failures and two maintenance lint/test-quality findings. Request scope/contract decisions for the additional failures and approved integration test environment. No build-ready claim, checkpoint commit, corrected image, deployment or soak. Fedora remains stopped on the persistently contained candidate

### Tech Lead resumed checkpoint expectations

PMA paused Developer and authorized exclusive Tech Lead review, product-only checkpoint/non-force main push, exact clean build and contained Fedora deployment without rollback. Maintenance tools and security refactors are expressly excluded. Isolated unpatched baseline comparison classified all 15 failures: five inherited-endpoint cache-shape failures disappear, one LazyMCP assertion omitted the required nullable toolset field, and nine provider-dependent failures reproduce without credentials/network on both revisions. Corrected only the stale product assertion. Focused isolated matrix: 229 passed, no skips. See logs/13-isolated-baseline-review.md. No all-suite pass is claimed. Live Fedora matrix/900-second soak remain required and NAS remains prohibited
