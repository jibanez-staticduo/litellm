---
id: TASK-2026-08-25-007-build-stage-deepseek-policy-image
complexity: complex
track: implementation
slice: foundation
status: blocked
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-007 - Build and Stage DeepSeek Policy Image

## Objective
Build a content-addressed immutable LiteLLM image from the reviewed source, deploy it only to stopped NAS staging, and validate the full DeepSeek contract before production promotion.

## Acceptance Criteria
- [ ] AC-1: Capture source revision/diff identity, prior staging/production image digests, config checksums, service state, and exact rollback commands without secrets.
- [ ] AC-2: Build and identify one immutable image containing only the reviewed task-owned source changes plus required repository state.
- [ ] AC-3: Deploy only to NAS staging, preserving dependencies, database ownership, model records, credentials, and production services.
- [ ] AC-4: Verify staging health, model identity, inventory, and restart persistence.
- [ ] AC-5: Probe canonical upstream controls `none`, `low`, `high`, and `max`, then public Chat and Responses `off`, `low`, `high`, `max`, `medium`, and `xhigh` for both target aliases.
- [ ] AC-6: Prove rejected public values return deterministic 400 errors and do not reach DG1 using request-scoped evidence.
- [ ] AC-7: Verify one unrelated hosted-vLLM reasoning model retains prior behavior.
- [ ] AC-8: Produce complete evidence and an explicit production promotion recommendation or rollback report.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-007-build-stage-deepseek-policy-image/` with:
- `SUMMARY.md` mapping AC-1 through AC-8.
- `logs/` with redacted build, digest, staging, health, restart, request matrix, and rollback evidence.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** baseline capture
  - **Evidence:** evidence logs
- [ ] AC-2
  - **Method:** immutable image build and digest inspection
  - **Evidence:** evidence logs
- [ ] AC-3
  - **Method:** staging-only deployment inspection
  - **Evidence:** evidence logs
- [ ] AC-4
  - **Method:** health and restart checks
  - **Evidence:** evidence logs
- [ ] AC-5
  - **Method:** direct and staged API probes
  - **Evidence:** evidence logs
- [ ] AC-6
  - **Method:** correlated rejection/log checks
  - **Evidence:** evidence logs
- [ ] AC-7
  - **Method:** non-regression probe
  - **Evidence:** evidence logs
- [ ] AC-8
  - **Method:** evidence review
  - **Evidence:** SUMMARY.md

## Blocker Report
- Candidate image built successfully as `docker.staticduo.com/litellm@sha256:a8cf0e9d64be4f6fec1ab517c560b7619f8c6a8df60adcc52f48ccfb5d1d288e`.
- Staging startup is blocked before port 4000 opens by a pre-existing ChatGPT refresh-token 401/device-auth flow.
- Staging was fully restored to its prior digest and stopped state; production and clients were not touched.
- Resume this same task after staging authentication/startup isolation is repaired.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- The reviewed source was built from a clean base-revision archive plus a recorded runtime patch into immutable image `docker.staticduo.com/litellm@sha256:a8cf0e9d64be4f6fec1ab517c560b7619f8c6a8df60adcc52f48ccfb5d1d288e`
- Deployment changed only the stopped NAS staging service and preserved production, Fedora, client configs, staging data services, database ownership, model records, and credentials
- The staging health gate failed because the existing startup/auth wrapper entered device authentication after a ChatGPT refresh-token 401; the proxy never opened port 4000
- Rollback restored the exact prior staging Compose checksum and immutable image, then returned staging to stopped state. Production remained healthy and unchanged
- AC-1, AC-2, AC-3, and AC-8 pass; AC-4 fails; AC-5 through AC-7 were halted by the required health stop condition
- Production promotion is explicitly rejected. PMA should route staging credential repair or reauthentication, then reopen this task for the complete live matrix
