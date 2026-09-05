# TASK-2026-09-03-011 Evidence Summary

## Summary

PASS investigation. Source confirms `defend_memory-find` intentionally reenters the same Fedora LiteLLM process for one embedding and bounded reranking while the original LazyMCP request remains open. The deterministic path does not call LazyMCP or the memory-agent gateway again, so source alone proves reentry but not recursion

The highest-ranked failure model is candidate-specific nested model routing or callback/cache feedback that turns this reentrant edge into repeated same-route requests. Deterministic-memory fan-out and request/result retention would amplify that cycle. A single nominal find is too bounded to explain approximately 100 GiB in LiteLLM: documents are clipped, output is compact, Qdrant vectors are excluded, and normal embedding/rerank responses are small

## Work Performed

- Read the task frontmatter, governing SCR, parent execution result, prior kernel/runtime evidence, diagnostic runbook, DCR bootstrap, architecture contract, relevant CodeMaps, and source across LiteLLM and agent-memory-platform
- Traced public LazyMCP routing, ASGI streaming bridge, session manager, tool listing, permission/guardrail path, MCP client/session transport, Defend deterministic retrieval, Qdrant/Neo4j fan-out, embedding/rerank callbacks, provider routing, response handling, cache behavior, and cancellation boundaries
- Compared candidate source `bf58974a935521fa570fa7e280c51a00b2e5b54e` with rollback source `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95` at the relevant route, MCP, Router, cache, HTTP, and provider boundaries
- Ranked recursion, fan-out, buffering, transport/session, retry, and direct-allocation hypotheses with supporting and contradictory evidence
- Defined exact secret-free route-cardinality, selected-deployment, egress-authority, socket/task/thread, memory, and cancellation-drain observations for the one-call maintenance retry
- Defined isolated regressions and conditional minimal corrections without changing source, configuration, production, credentials, or deployments

## Acceptance Criteria Coverage

- **AC-1: PASS.** `.staticeng/evidences/TASK-2026-09-03-011-investigate-reentrant-memory-path/logs/01-call-graph-and-ranked-hypotheses.md` traces the full client -> LazyMCP -> LiteLLM MCP manager -> Defend deterministic find -> Fedora LiteLLM embedding/rerank -> provider -> return path
- **AC-2: PASS.** The evidence ranks all requested hypotheses and distinguishes likely root cause from amplifiers and low-probability standalone explanations
- **AC-3: PASS.** Candidate and rollback are compared at source and preserved config-shape boundaries without secret values; the unresolved selected-deployment/upstream-authority equality is explicit
- **AC-4: PASS.** The evidence defines bounded live instrumentation for one request plus isolated cancellation, recursion, cache, and RSS regressions
- **AC-5: PASS.** The likely minimal fix is conditional on the first repeated nested route or failed drain boundary; the immediate recommendation is a single instrumented probe and rollback, with no mutation performed

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. This task records an unresolved incident investigation and does not change supported behavior or maintained source structure

## Open Risks

- The exact allocation stack remains unproven because no candidate request or heap/stack sample was taken in this task
- Existing evidence compares model/fallback projections but not the selected nested deployment ID and normalized egress authority under candidate versus rollback
- `graph_top_k=0` still runs the Neo4j lane and its rerank, and `candidate_k=5` can still fetch 80 Qdrant candidates because default filter fields make the filtered branch active
- The MCP call timeout relies on cancellation propagating through gather, the MCP SDK task group, transport, Defend, and nested model requests; no production-equivalent regression currently proves full drain
- Fedora has no cgroup memory ceiling, so the existing independent watchdog remains mandatory and candidate exposure remains unsafe without it

## Recommended Next Step

PMA should add the route-cardinality and normalized egress-authority counters from `.staticeng/evidences/TASK-2026-09-03-011-investigate-reentrant-memory-path/logs/01-call-graph-and-ranked-hypotheses.md` to TASK-007's already authorized single-call retry, then hand TASK-010's headless authorization precondition and TASK-007's diagnostic contract to Tech Lead. Roll back immediately if the candidate receives more than one nested embedding, more than three nested reranks, any nested LazyMCP request, any continued arrivals after settlement, or any existing watchdog threshold. Do not send a second diagnostic request

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-011 PASS. Source confirms the outer LazyMCP `defend_memory-find` holds Fedora LiteLLM open while Defend deterministically calls that same LiteLLM for one embedding and up to three reranks. The deterministic path does not call LazyMCP or the memory-agent gateway again, so recursion is not intrinsic. Candidate-only nested model routing or callback/cache feedback is the leading hypothesis; deterministic fan-out and buffering are likely amplifiers, while retry, transport cleanup, and one-shot direct allocation rank lower. Add secret-free per-route cardinality and selected-deployment/egress-authority equality to TASK-007's one-call watcher. Expected maxima are one nested embedding and three nested reranks, with no nested LazyMCP and complete task/socket drain within 15 seconds. Any excess count or continued arrival proves multiplication and requires immediate rollback. No production request, secret read, source/config/host mutation, or deployment occurred
