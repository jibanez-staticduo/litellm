# NAS Stream-Safe 1.98.0 Deployment Evidence

## Summary

The NAS release is **APPROVED AND RUNNING** after Reopen 4. NAS runs the exact immutable 1.98.0 candidate through the migrated wrapper, with every functional, LazyMCP, topology, credential, observation, persistence, preservation, and isolation gate passing. Earlier attempts and their automatic rollbacks remain recorded below as release history

Fedora remained unchanged on its inherited pre-release digest and stable remained unresolved/untouched, as required by the Reopen 4 isolation boundary. The tested NAS rollback image, wrapper/Compose pair, and account3 restoration backup remain protected and available

## Reopen 1 Result

Tech Lead approved exactly one corrected redeployment. The fresh T0, manifest/config identity, candidate health, immediate credential metadata, exact topology, dependency, mount, and network gates passed. One approved lock path advanced only ctime as expected

The first functional request returned HTTP 200, but the harness then attempted to parse the native Responses event lifecycle as JSON because the client request specified `stream=false`. This was a harness false assumption: the previously accepted release contract records HTTP 200 `text/event-stream` and a native Responses lifecycle for this probe. The mandatory stop nevertheless fired before the remaining Codex and LazyMCP gates, and NAS automatically restored the exact 1.92.0 image plus wrapper/Compose pair. The one authorized attempt is exhausted, so final promotion remains **REJECTED** without another retry

## Reopen 2 Result

The final Tech Lead-authorized attempt used Content-Type-driven SSE parsing. The native client `stream=false` request and direct default Codex request each returned HTTP 200 `text/event-stream` with nine valid blank-line-delimited JSON events, ordered created/in-progress/completed lifecycle, one terminal event, consistent response IDs and contiguous sequence numbers, correct deployment selection, and no forbidden errors

The next direct account2 request returned HTTP 429 instead of the required HTTP 200. The mandatory stop fired before the public and LazyMCP gates, and NAS automatically restored the exact 1.92.0 rollback unit. A 10-minute rollback observation passed. The final authorized retry is exhausted, so cross-host promotion remains **REJECTED**

## Reopen 3 Result

Reopen 3 applied Tech Lead's exact account2 quota disposition. Native `stream=false`, direct default, and public default-primary requests each passed HTTP 200 with the complete nine-event SSE contract and correct selection. Direct account2 returned the allowed provider-quota HTTP 429 with correct account2 selection and no forbidden error category. The full LazyMCP status, describe, three-tool list, and harmless `memory-find` smoke passed

After the 10-minute candidate interval, credential metadata, exact candidate identity, and exact 32-model/16-rule topology still passed. A subsequent assertion inside the final observation aggregate failed before the success marker. The harness did not persist the individual failed assertion or sanitized candidate log category before automatic rollback removed the candidate container, so release acceptance cannot be established. NAS was rolled back and passed another 10-minute rollback observation. Reopen 3 authorization is exhausted and promotion remains **REJECTED**

## Reopen 4 Result

Reopen 4 implemented the Tech Lead atomic evidence-first contract before mutation. Attempt `reopen4-20260819T020916Z` persisted every required functional and observation sub-gate as an atomic artifact/result pair under the protected host release directory, including expected/actual values, status, classification, container identity, artifact path, and SHA-256. A canonical aggregate was persisted before acceptance

All required sub-gates and the aggregate passed. The external chain contains 19 result records with all 19 supporting artifact hashes independently verified. Sanitized candidate-log categories were persisted before success; concrete stream, auth, device-flow, migration, schema, and patch failures were zero. Generic tracebacks were retained as an audit count but were not themselves treated as a concrete blocking category under the approved account2-quota contract

NAS remains healthy on candidate manifest `42d365...115b` and config/image ID `45a019...c73`, with zero restarts/OOM and five expected mounts. Promotion status is **APPROVE NAS**

## Work Performed

- Captured three fresh T0 gates within 60 seconds of each attempted recreation; each had safe 0700/0600 auth permissions, zero preceding 15-minute auth/device-flow failure matches, exact 32-model/routing hashes, unchanged dependency IDs, and tested rollback artifacts
- Pulled and selected only immutable candidate manifest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, then recreated only NAS `litellm` with `--no-deps`
- Applied the mandatory rollback after each failed assertion, restoring NAS digest `sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018` plus wrapper/Compose hashes `ada13e55...c8778` and `e55a6827...4129`
- Restored Fedora to pre-release digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9` after the first failed NAS release attempt
- Stopped after three attempts and requested Tech Lead help through PMA as required
- Executed one Reopen 1 attempt with corrected identity/lock gates and one final Reopen 2 attempt with the Content-Type-driven SSE parser; both automatic rollbacks passed
- Executed Reopen 3 to prove the full functional/LazyMCP matrix, then Reopen 4 with atomic per-sub-gate evidence persistence; Reopen 4 passed and remains deployed

## Acceptance Criteria Coverage

- **AC-1: PASS**. Fresh T0 passed with safe auth metadata, corrected lock handling, zero recent auth/device failures, exact topology/dependencies, and rollback readiness
- **AC-2: PASS**. NAS runs the immutable 1.98.0 manifest/config/version/revision through the migrated wrapper; only LiteLLM was recreated
- **AC-3: PASS**. Health/readiness/liveliness, zero restart/OOM, ten-minute observation, startup/preservation, and concrete clean-log gates passed with atomic per-sub-gate evidence
- **AC-4: PASS**. Exact 32-model and 16-rule hashes, default/account2/public topology, zero account3, protected hashes, credential metadata, dependencies, five mounts, and two networks are preserved
- **AC-5: PASS**. Native `stream=false`, direct default, allowed direct account2 quota response, and public default-primary passed exact selection and SSE/error assertions
- **AC-6: PASS**. LazyMCP status, describe, exact three-tool list, and harmless configured `memory-find` smoke passed
- **AC-7: PASS REOPEN ISOLATION**. Fedora remained healthy and byte-for-byte unchanged on its inherited pre-release baseline; stable remained unresolved and untouched
- **AC-8: PASS, APPROVE NAS**. Complete historical rollback proof and the final atomic evidence-first deployment packet support NAS promotion

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. No application source changed; this evidence records operational deployment and rollback truth

## Open Risks

- Account2 remains provider quota/rate limited and may be unavailable as fallback until external quota recovers; default/public functionality is healthy
- Fedora remains on its inherited pre-release digest because Reopen 4 required isolation, so PMA must account for that state in cross-host release closure
- Stable remains unresolved exactly as inherited from the preceding tasks
- `staticeng_validate` remains blocked by pre-existing broken links and repository-wide missing CodeMaps; repair dry-run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA should advance the successful NAS deployment to cross-host QA/closure while preserving the stable-tag hold. Record Fedora's inherited pre-release digest explicitly before deciding any separate Fedora alignment action
