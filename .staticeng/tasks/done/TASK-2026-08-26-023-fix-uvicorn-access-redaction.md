---
id: TASK-2026-08-26-023-fix-uvicorn-access-redaction
complexity: standard
track: implementation
slice: logic
status: done
scr: null
parent: TASK-2026-08-26-022-diagnose-lazymcp-log-errors
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-26-023 - Fix Uvicorn access-log redaction

## Objective
Preserve Uvicorn's structured access-log argument contract while retaining secret redaction, eliminating formatter tracebacks without changing request behavior.

## Acceptance Criteria
- [x] AC-1: `SecretRedactionFilter` preserves the five-element Uvicorn access-record argument structure and value types while redacting sensitive string content.
- [x] AC-2: A focused regression test formats a filtered Uvicorn access record with the real `uvicorn.logging.AccessFormatter` without exception and verifies redaction plus normal status/path output.
- [x] AC-3: Malformed `uvicorn.access` argument shapes and redaction exceptions fail closed without emitting raw data or reaching an incompatible formatter.
- [x] AC-4: Existing secret-redaction and LazyMCP focused tests pass with no skipped tests.
- [x] AC-5: The candidate is independently reviewed before deployment.
- [x] AC-6: Production remains healthy, `/lazymcp` succeeds, and a bounded post-deployment log check contains no matching formatter traceback or leaked probe secret.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/` with:

- `SUMMARY.md` mapping AC-1 through AC-6 to verification results.
- `logs/` containing focused test, deployment health, LazyMCP probe, and bounded clean-log outputs with secrets redacted.

Product documentation is not required because this is an internal logging compatibility correction.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** code review and focused unit test
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/SUMMARY.md`
- [x] AC-2
  - **Method:** focused regression test
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/logs/`
- [x] AC-3
  - **Method:** focused fail-closed unit tests
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/logs/`
- [x] AC-4
  - **Method:** focused automated tests
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/logs/`
- [x] AC-5
  - **Method:** independent technical review
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/SUMMARY.md`
- [x] AC-6
  - **Method:** production smoke and bounded log observation
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-26-023-fix-uvicorn-access-redaction/logs/`

## Approved Implementation Design

For the exact logger name `uvicorn.access`, preserve Uvicorn 0.51.0's five-element positional tuple. Redact every string element independently, preserve non-string values and their types, redact the format string without resolving its placeholders, and validate that `record.getMessage()` still succeeds. If the tuple shape is unsupported or redaction/validation fails, return `False` and drop the record fail-closed.

All other loggers retain the current generic behavior that renders the message, redacts it, and clears `record.args`. Do not change filter registration, dependencies, routes, request handling, JSON logging, or CodeMaps.

## Implementation Sequence

1. Add the exact `uvicorn.access` branch in `SecretRedactionFilter.filter()` before generic preformatting.
2. Preserve a valid five-element tuple, redact string members, preserve numeric status, and validate formatting.
3. Drop malformed access records and redaction failures fail-closed.
4. Add real `AccessFormatter`, structured-args, malformed-shape, and redaction-failure regression tests in `tests/test_litellm/test_secret_redaction.py`.
5. Run the new focused cases, the complete mapped redaction module, focused LazyMCP tests, and changed-file lint/type checks.
6. Produce the implementation Evidence Packet and hand back for independent review; do not deploy.

## Handoff
[Agent Message] From: product_manager To: developer

The task is authorized for implementation. Follow the approved design and sequence above. Make the minimum change in `litellm/_logging.py`, extend only `tests/test_litellm/test_secret_redaction.py`, and produce the required Evidence Packet. Do not deploy or commit; hand the exact candidate back to PMA for independent review.

# Post Implementation Task Updates

## Reopen History

- Reopen 1, 2026-08-27: Independent review returned NO-GO because traceback redaction failures were swallowed, extra-field redaction failures could escape, and the original single forced-failure test exercised only message redaction. The candidate was reopened to make all `uvicorn.access` redaction stages fail closed and add stage-specific handler regressions

## Developer: Post Implementation Expectations

- Implemented the approved exact-name `uvicorn.access` branch in `SecretRedactionFilter.filter()`
- Preserved and independently redacted Uvicorn's five positional arguments, retained non-string types, and validated `record.getMessage()` before allowing emission
- Added real `AccessFormatter`, structured argument, malformed shape, and forced redaction-failure regressions
- Verified 7 focused regressions, all 40 mapped redaction tests, and all 287 focused LazyMCP server tests with no skips or failures
- Verified changed-file Ruff lint/format, Python compilation, diff whitespace, and zero basedpyright diagnostics in changed regions
- Retained the aggregate type-gate and StaticEng validation baseline limitations in the evidence packet without modifying unrelated concurrent worktree artifacts or CodeMaps
- AC-1 through AC-4 are implementation-complete; AC-5 independent review and AC-6 deployment/production verification remain pending
- Product documentation is not required for this internal logging compatibility correction

## Developer: Post Implementation Expectations, Reopen 1

- Extended only the `uvicorn.access` branch so traceback and extra-field redaction execute inside the same fail-closed boundary as message and tuple-member redaction
- Preserved generic logger behavior unchanged
- Replaced the overstated single failure regression with separate message, tuple-member, traceback, and extra-field failure cases; every case proves no handler output and no escaped exception
- Verified 10 focused regressions, all 43 mapped redaction tests, and all 287 focused LazyMCP server tests with no skips or failures
- Verified changed-file Ruff lint/format, Python compilation, diff whitespace, and zero basedpyright diagnostics in the Reopen 1 changed regions
- AC-1 through AC-4 are implementation-complete after Reopen 1; AC-5 requires independent re-review and AC-6 remains pending deployment authorization and production verification
- Product documentation and CodeMap changes remain unnecessary for this scoped internal correction

## Developer: Post Implementation Expectations, AC-6

- Tech Lead Reopen 1 review returned GO before any deployment mutation
- Captured the previous immutable image digest and image ID, Compose/config checksums, health, and exact rollback command before building or deploying
- Built an isolated uniquely tagged image from the current revision plus tracked runtime diffs, excluding test diffs and untracked shared-worktree CodeMaps/evidence from source assembly; normal Docker ignore rules remained active
- Published and deployed immutable candidate `docker.staticduo.com/litellm@sha256:8a688990cb66fa7bd804fc8ac7423dd487dfd876d10fa7ef384096ab373ff6e5`
- Recreated only the NAS `litellm` service through `/volume2/docker/litellm`; unrelated services and persistent configuration were unchanged
- Verified running/healthy status, zero restarts, OOM false, readiness HTTP 200, connected LazyMCP status, and expected redacted `/lazymcp` access output
- Verified the bounded candidate log window contains zero raw probe-marker occurrences, zero `Logging error` entries, and zero `cannot unpack non-iterable NoneType object` entries
- AC-1 through AC-6 now pass; rollback was not required
- No git commit, git push, task archive, registry edit, or unrelated worktree modification was performed

## Product Manager: Final Closure

- Accepted Tech Lead Reopen 1 GO and the complete AC-1 through AC-6 evidence chain
- Confirmed immutable production deployment, healthy runtime, successful connected LazyMCP status, redacted access output, and bounded clean logs
- Confirmed product, architecture, technical documentation, and CodeMap updates are not required
- Archived the task and updated the task registries; source commit remains pending
