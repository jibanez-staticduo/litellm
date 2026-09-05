# Proven retry-breadcrumb ownership of completed requests

## Clock correction

The earlier approximate "2.5 hours" age in log 16 compared unlike local/UTC clock displays and must not be used as uptime evidence. Its monotonic 261.95-second trial and byte measurements remain valid. This continuation uses UTC container timestamps and monotonic trial durations, not that age estimate

## Initial running-process counts

Continued on e340ea66, container start 2026-09-05T10:40:48.540152624Z, restart count zero. A same-host UTC check returned 2026-09-05T11:28:25Z. Initial cgroup current 1660104704, anon 1570885632, file 63606784, kernel 24383488 bytes. Python process VmRSS 1562484 KiB, RssAnon 1516472 KiB, RssFile 46012 KiB, 11 threads. This is anonymous process growth, not file-cache growth

Small caches: 7 API-key, 13 router and 1 logging-cache entry. Async tasks varied with live MCP sessions (41 at one sample, including 8 each of stateless-server/message-router/receive-loop). Only one logging worker and one spend monitor existed

## Lightweight allocator and ownership sample

Used installed GDB and CPython APIs, with short attach deadlines and explicit detach, to enable one-frame tracemalloc briefly and print numeric queue counts. No source or debug endpoint was added. Temporary diagnostic code was passed in memory; no new harness, request dump or heap artifact was created

An initial queued pending-call attempt did not execute promptly. Its buffer was replaced with a no-op before continuing. Subsequent bounded evaluations ran while the interpreter held the GIL; later samples used a one-shot interpreter-frame breakpoint rather than processing arbitrary network payloads. Per-evaluation temporary C buffers were freed. The first 4-KiB no-op pending buffer remains process-local until recreation. Tracing was explicitly stopped and a later sample confirmed trace_active=false. All diagnostic state disappears on the corrected-image recreation

Logging queue/running/dequeued counts were **0/0/0** at both ends. Spend queue **1**, tool queue **0**, retry breadcrumbs **4**. Thus a growing logging/spend backlog was not the retaining owner

The bounded trace interval included a 120-second no-operator-model-call wait. Top still-live allocations since tracing began, excluding the sampling endpoint and diagnostic code:

| Allocation location | Bytes | Allocations |
| --- | ---: | ---: |
| http_parsing_utils.py:94, orjson.loads(request body) | 80701218 | 114749 |
| starlette/requests.py:259, request body | 29003990 | 262 |
| httpx/_content.py:179, outbound body | 28707661 | 45 |
| sensitive_data_masker.py:182 | 12706712 | 59239 |
| pydantic/main.py:475 | 5813242 | 71276 |

Tracer bookkeeping itself was 39273328 bytes and is not counted as product retention. The diagnostic endpoint's object-list allocation was excluded from attribution

Count-only referent inspection found **1373 Starlette Request objects**, with **171099265 body bytes**. Completed requests were retained by frames in chat_completion, base_process_llm_request and _process_llm_request. Following traceback ownership found RouterRateLimitError held by completed acompletion Task, _GatheringFuture, logging exception dictionaries and router retry frames

A single explicit GC cycle was used only as an ownership diagnostic, not as a fix or a stability result: it collected 152208 objects, while Request count changed only 293 -> 292 at that later sample. Earlier and later request counts are different snapshots under concurrent traffic, not one GC delta. GC thresholds were not changed

The decisive direct path was captured for three current breadcrumbs:

```text
router.previous_models[0].litellm_logging_obj.model_call_details.exception
  .__traceback__.chat_completion.locals.request   body_bytes=257811
router.previous_models[1].litellm_logging_obj.model_call_details.exception
  .__traceback__.chat_completion.locals.request   body_bytes=257811
router.previous_models[2].litellm_logging_obj.model_call_details.exception
  .__traceback__.chat_completion.locals.request   body_bytes=257811
```

The Router is a long-lived root. Its four breadcrumbs held live Logging objects; those retain exception/request graphs and snapshots of earlier retry history. The count of breadcrumb entries can remain four while the referenced graph grows. Two broader bounded graph traversals reached their 20000-node cap without a result; no conclusion was taken from them. The direct field/traceback path above establishes ownership without that inference

## Minimal correction and reproduction

Added only `litellm_logging_obj` to the existing RETRY_BREADCRUMB_EXCLUDED_KWARGS set in router.py. Like original_function, a live logging owner is runtime state rather than attempt diagnostics. Model, exception type/string, metadata and existing retry behavior are preserved. No exception mutation, traceback clearing, retry change, GC policy, security masker change or client parameter policy change was made

New mapped test_retry_breadcrumb_lifetime.py records 25 failures, with real Logging and Starlette Request objects and prior-history snapshots, for both metadata and litellm_metadata. Weak references distinguish reachable retention from ordinary collectable cycles. Both cases fail without the exclusion even after GC. Both pass with it: completed Request/Logging objects are released, the history stays at four and diagnostic fields are preserved

Verification: **337 focused tests passed**, no skips, seven existing warnings. Existing log_retry test separately passed (139 unrelated cases deselected). Direct Ruff passed; test formatting was normalized. StaticEng validation is required before checkpoint

## Next gate

Commit/build exact source, recreate Fedora contained without rollback (also removes temporary in-process diagnostics), then run repeated equivalent successful and rejected-request batches plus real SDK/model/MCP checks and natural drain/soak. Do not transfer pre-fix or forced-GC observations into a final stability PASS
