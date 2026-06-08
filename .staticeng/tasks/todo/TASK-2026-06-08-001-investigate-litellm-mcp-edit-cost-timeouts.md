---
id: TASK-2026-06-08-001
title: Investigate production LiteLLM MCP edit failures and cost timeouts
status: active
complexity: standard
track: investigation
slice: qa
assigned_to: qa_engineer
handoff_from: product_manager
created_at: 2026-06-08
scr: none
parent: none
---

# Task: Investigate Production LiteLLM MCP Edit Failures and Cost Timeouts

## Classification

- Complexity: `standard`
- Track: `investigation`
- Slice: `qa`

## User Problem

Production LiteLLM is deployed from the main-based release flow: it takes current upstream LiteLLM, merges the private `litellm-production-main` / `staticduo-production-main` changes, and deploys that tree.

Current production symptoms:

- Editing an MCP in production fails/crashes.
- Loading charges/costs appears to timeout.

## Acceptance Criteria

- AC-1: Confirm deployed image, health, DB status, and current production source SHA if possible.
- AC-2: Capture recent sanitized LiteLLM logs around MCP edit/admin/cost/spend failures.
- AC-3: Check read-only admin/API endpoints for MCP server list/detail/update-related metadata where safe; do not mutate MCPs.
- AC-4: Check cost/spend endpoints read-only and DB table size/query behavior to explain timeout.
- AC-5: Inspect relevant source paths in current production branch for likely failure points.
- AC-6: Provide root cause hypotheses ranked by evidence and recommend safe fixes versus changes requiring deploy.

## Constraints

- Read-only production investigation only.
- Do not edit MCPs.
- Do not change LiteLLM config, DB, Docker, or deploy.
- Do not print secrets, API keys, auth headers, env vars, DSNs, cookies, or raw prompts.
- Sanitize private user/key/team metadata.

## Expected Evidence

Return concise evidence:

- Commands/endpoints used, sanitized.
- Log error categories/counts.
- Endpoint behavior and timeout behavior.
- DB row/table size summaries.
- Source files/functions inspected.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Investigate production LiteLLM MCP edit failures and cost/charge timeouts read-only. Correlate live logs/endpoints/DB stats with current deployed source. Do not mutate MCPs or production state.
