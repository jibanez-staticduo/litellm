---
id: SCR-2026-08-28-001-resilient-lazymcp-discovery
status: proposed
requested_by: product_manager
approved_by: null
date: 2026-08-28
---

# SCR: Resilient LazyMCP Discovery

## Observed Baseline

- A bounded production investigation found 27 registered servers but only 149 tools in unrestricted aggregate discovery
- Isolated per-server discovery recovered 537 tools; one server remained sensitive to the existing approximately five-second boundary
- The runtime stayed healthy and the earlier access-log traceback did not recur. The discovery regression was consistent with shared aggregate timing and degraded-result caching, not a total service failure
- Server identities, endpoints, credentials, authorization material, tool arguments, and payloads are intentionally omitted

## User-Visible Behavior

- Discovery returns tools from every healthy server that completes within its own bounded attempt, even when another server is broken, slow, unauthorized, unavailable, optional, or disabled
- Failure of one server removes or marks stale only that server's tools. It must not produce an empty or broadly reduced successful cache entry for healthy siblings
- A degraded response remains successful and usable when at least one permitted server succeeds. It identifies degraded status and per-server outcomes through the supported status/reporting surface without exposing sensitive detail
- Results and status are deterministic for the same completed attempts: each server has one current classified outcome, whether cached tools are fresh or stale, and a redacted reason suitable for an operator
- A later successful attempt replaces that server's degraded state and is reported as recovered without requiring a process restart or broad cache flush

## Classified Outcomes

The supported status/reporting surface must use stable machine-readable outcome codes. Human-readable text may add safe context but must not replace or vary these codes

| Outcome code | Meaning | Retry and cache treatment |
| --- | --- | --- |
| `discovered` | Current attempt returned a valid tool listing | Store as that server's fresh positive result |
| `timeout` | The per-attempt deadline elapsed | Retry once at most; retain eligible last-known-good tools as stale |
| `authentication` | Credentials are missing, expired, rejected, or require user action | Do not retry automatically; retain eligible stale tools only when policy still permits visibility |
| `permission` | Identity is valid but lacks required server or tool access | Do not retry automatically; do not expose tools the current identity is not permitted to see |
| `connectivity_external_dependency` | Network, DNS, upstream availability, rate limit, or other external dependency prevented discovery | Retry once at most when transient; retain eligible last-known-good tools as stale |
| `protocol_version` | Response framing, schema, transport, or negotiated protocol/version is unsupported or invalid | Do not retry automatically; retain eligible stale tools |
| `configuration` | Registration or non-secret runtime configuration is invalid or incomplete | Do not retry automatically; retain eligible stale tools only when still policy-safe |
| `adapter_internal_error` | LazyMCP or adapter logic failed outside the preceding classes | Do not retry automatically; retain eligible stale tools and emit an internal diagnostic correlation ID |
| `optional_disabled` | Server is intentionally optional, quarantined, or disabled | Do not attempt or retry; exclude its tools from the active listing |
| `recovered` | Current discovery succeeded after that server's recorded degraded outcome | Replace stale data with the fresh result, then return to `discovered` after the configured observation window |

Classification precedence is `optional_disabled`, `authentication`, `permission`, `timeout`, `protocol_version`, `configuration`, `connectivity_external_dependency`, then `adapter_internal_error`. Unknown exceptions fail closed into `adapter_internal_error`; they must not be exposed verbatim

## Isolation, Timeouts, and Concurrency

- Each server executes in an isolated failure boundary. Exceptions, cancellation, timeout, parsing, and cache writes are contained to that server
- Discovery uses a finite configurable concurrency cap, a per-attempt deadline, and a global request deadline. Defaults and overrides must be recorded in redacted evidence and covered by boundary tests
- Work not started before the global deadline is classified `timeout`; cancellation must not discard completed sibling results
- Only `timeout` and transient `connectivity_external_dependency` receive one automatic retry at most, with bounded backoff and jitter inside the global deadline. Authentication, permission, protocol, configuration, internal, optional, and disabled outcomes receive no automatic retry
- Concurrent requests must coalesce equivalent in-flight discovery per server or enforce an equivalent bound so retries and callers cannot multiply upstream work without limit

## Cache Contract

- Cache keys and writes are per server and authorization scope. Results from one identity or permission scope must never be served to another
- A valid positive result has a configured fresh TTL and maximum stale age. Both values are finite, observable without secret values, and tested at their boundaries
- A failed, timed-out, malformed, cancelled, or not-started attempt never overwrites that server's last-known-good positive entry and never writes a broad aggregate negative entry
- Within maximum stale age, transient, protocol, configuration, or internal failures may serve the permitted last-known-good tools for only that server, explicitly marked stale with age and current outcome. After maximum stale age, those tools are omitted
- Authentication and permission failures never use stale data to bypass current access policy. Stale tools are served only if the current identity remains authorized through an independent local policy decision
- A server with no eligible positive entry contributes no tools, while healthy siblings remain fresh. Recovery atomically replaces stale data for that server and invalidates any derived aggregate view
- Manual invalidation and rollback may clear task-owned discovery cache entries, but neither operation may alter registrations, credentials, permissions, or unrelated cache namespaces

## Final Server Disposition

Release evidence must record redacted before/after tool counts and exactly one final disposition for every server affected in the baseline or during verification

| Final disposition | Required evidence |
| --- | --- |
| `recovered` | Valid isolated and aggregate discovery, with the after count and any stale state cleared |
| `optional/disabled` | Approved operational decision and proof the server cannot degrade siblings |
| `blocked by authentication` | Authentication or permission outcome, required owner action, and proof healthy siblings remain available |
| `blocked by external dependency` | External dependency outcome, bounded observation, owner/follow-up, and proof healthy siblings remain available |

Protocol, configuration, or adapter/internal outcomes are release-blocking defects, not final external-dependency dispositions. They must be corrected and reported as `recovered`, or explicitly reclassified with evidence before release

## Non-Goals

- No changes to server registrations, tool definitions, credentials, grants, authorization policy, or upstream MCP implementations
- No guarantee that an unavailable server's tools are current, and no indefinite stale serving
- No unbounded retries, concurrency, wait time, stale age, background work, or cache growth
- No suppression of degraded state, no conversion of failures into an apparently complete empty result, and no disclosure of raw exceptions or upstream payloads
- No redesign of tool invocation behavior beyond preserving the authorization boundary used by discovery

## Release, Verification, and Rollback

- Focused tests cover every outcome code, classification precedence, isolated sibling success, cancellation, deadlines, retry bounds, request coalescing, authorization-scoped cache keys, stale expiry, recovery, and redaction
- Regression tests reproduce the 27-server partial-discovery shape with deterministic fakes, including a server at the deadline boundary. All required focused and regression tests pass with zero skips and zero failures
- Independent review verifies behavior, security/redaction, bounded resource use, test quality, and AC traceability before publication
- Publication uses one immutable image attributable to the reviewed commit. Fedora and NAS deploy the identical digest; mutable tags are not deployment evidence
- Post-deploy observation is bounded and records host health, aggregate totals, per-server before/after counts, stale use, retries, latency/deadline behavior, redacted outcome codes, and final dispositions. No credentials, authorization material, endpoints, tool payloads, prompts, responses, or raw exception text are retained
- Before deployment, record the prior immutable digest and exact host-specific rollback commands. Rollback redeploys that prior digest to both hosts, clears only incompatible task-owned discovery cache entries if required, verifies health and healthy-server discovery, and preserves registrations, credentials, permissions, databases, and unrelated configuration

## Documentation Impact and Source of Truth

- Steady-state technical documentation must change because discovery isolation, outcome codes, timeout/concurrency bounds, cache semantics, and operator dispositions are durable contracts
- The implementation must create `.staticeng/docs/architecture/resilient-lazymcp-discovery-contract.md`; after approval and rollout, that file is the steady-state technical source of truth and this SCR remains the decision record
- No separate user-facing product documentation is required unless implementation adds or changes a user-visible status field, code, or recovery action outside the existing supported reporting surface. Any such change must update the corresponding public/operator reference before release

## Numbered Acceptance Criteria

- **AC-1:** This SCR records the redacted observed baseline, user-visible behavior, non-goals, rollback expectations, and numbered acceptance criteria without claiming approval
- **AC-2:** A broken, slow, unauthorized, unavailable, optional, or disabled server cannot prevent completed healthy sibling listings, cache writes, or reporting
- **AC-3:** The supported reporting surface emits the stable redacted outcomes `discovered`, `timeout`, `authentication`, `permission`, `connectivity_external_dependency`, `protocol_version`, `configuration`, `adapter_internal_error`, `optional_disabled`, and `recovered` with the defined precedence
- **AC-4:** Discovery enforces finite per-attempt/global deadlines, finite concurrency, coalesced or equivalently bounded in-flight work, at most one transient retry, per-server authorization-scoped positive caching, finite stale use, and no broad transient false-negative cache writes
- **AC-5:** Release evidence records redacted before/after per-server counts and exactly one final disposition per affected server: `recovered`, `optional/disabled`, `blocked by authentication`, or `blocked by external dependency`; unresolved protocol, configuration, or adapter/internal defects block release
- **AC-6:** Focused and regression suites pass with zero skips/failures, independent review passes, one reviewed commit produces an immutable image, Fedora and NAS run its identical digest, bounded post-deploy observation passes, and documented rollback is verified ready
- **AC-7:** Implementation publishes `.staticeng/docs/architecture/resilient-lazymcp-discovery-contract.md` as the steady-state technical source of truth; public/operator documentation changes only when its supported user-visible contract changes

## Approval

Proposed for Product Owner review. No Product Owner approval is recorded
