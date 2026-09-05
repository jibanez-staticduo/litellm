# Reopen 1: active spend recursion and supported OAuth discovery

PMA resumed the same task for product logging. A fresh five-minute NAS log projection counted 148 RecursionError lines; retained frames contain only file/function/line identifiers, repeatedly spend_tracking_utils.py:821/784/786. No live payload, callback object or credential was inspected or retained

The sanitizer previously guarded dictionary identities but had no depth bound and did not track list identities. Local 2000-level dictionary/list chains and a self-referencing list all reproduced RecursionError before correction: three failed regressions. This establishes both the observed deep traversal failure and the unguarded list-cycle case without asserting that the private live payload was reconstructed

The correction bounds container depth at 32, extends identity tracking to list/tuple and typed model containers, preserves existing first-occurrence shared-dictionary semantics, and returns empty containers at repeated/depth boundaries. Arbitrary nonserializable runtime values become null without repr, str or attribute traversal. Normal scalar values, datetime encoding, string truncation and secret_fields exclusion remain intact. Caller-owned graphs and callbacks are not mutated

Typed response models are serialized through their declared model_dump representation and then sanitized. Temporary model dumps are held only until the sanitizer returns so Python cannot reuse an already-seen ID for a later independent model. A dedicated 20-model regression caught that intermediate implementation problem before release; all twenty token fields and callable identity now pass

## OAuth supported-flow finding

The missing _fetch_oauth_discovery_url is reached by supported RFC 9728 protected-resource discovery and issuer-anchored resource-scope discovery. It is not merely a dead test helper. History identifies the existing guarded fetch implementation in 51a3e90451 and its removal during integration. The repair restores the same-authority helper and shared fetch path at both resource and issuer metadata sites, using the existing async_safe_get implementation for federated URLs and disabling redirects for trusted same-authority URLs. No new trust policy, token, credential or auth-required outcome is introduced

A regression follows an actual-shaped 401 WWW-Authenticate resource_metadata challenge through resource metadata and issuer endpoints with origin guessing disabled. The full existing discovery guard class and the previously failing public cross-origin assertion now pass. No external provider credentials or service registrations were changed

## Verification

Full mapped files run in isolated Python processes, no skipped tests:

| File | Result |
| --- | --- |
| test_spend_tracking_utils.py | 181 passed, 6.52s |
| test_mcp_server_manager.py | 475 passed, 10.88s |
| test_mcp_server.py | 213 passed, 6.95s |
| test_router_model_cost_isolation.py | 82 passed, 10.84s |

Total: 951 passed. Existing Starlette/httpx and datetime.utcnow deprecations are retained. An initial single-process combined run exceeded its 180-second command deadline without an assertion failure being reported; it is not claimed as passing. The four complete isolated-file runs are the successful verification above, with no test changes to waive failures

Direct Ruff passes both changed production modules and the changed spend-test module. All four changed Python files pass Ruff formatting checks. Whole-manager-test Ruff additionally reports twelve existing import-order/deprecated-typing findings outside the new regression; those are not silently described as a clean whole-file lint pass or repaired as unrelated work. git diff --check passes

Normal spend payload/response coverage, nested secret-field filtering, callback nonmutation, dictionary cycles, shared dictionaries, typed response fields, deep dict/list chains and list self-cycles all pass. Repaired OAuth flow and all manager tests pass. Live correction, clean-source image build and Fedora-first/NAS verification remain pending at this source checkpoint
