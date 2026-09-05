# Fedora runtime repair: functional and bounded memory gates PASS

> PMA has accepted and archived this repair scope through [final workflow closure](../TASK-2026-09-05-003-close-dual-host-repair/SUMMARY.md). All execution-time identities, failures and holds below are preserved history; the closure index identifies the final accepted dual-host release

## Final approval and exact promotion subject

**Tech Lead approves Fedora functional/memory readiness and authorizes PMA NAS promotion** of:

`docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`

Exact source: `7a9ef0335303d973f3a228dcf7baadff18c82fb5`. Fedora is running/healthy, zero restarts/OOM, persistent 8-GiB/no-swap/restart=no. NAS was not accessed or changed

The final correction excludes live logging owners from retry breadcrumbs, breaking the proven traceback-to-completed-request root. 337 focused tests plus the existing retry test pass. Actual SDK JSON/stream, representative real models and MCP/LazyMCP calls pass. Twelve equivalent batches completed 120 successful JSON calls and 120 intended rejections without weakening error policy

Live traced allocations across loaded windows were 258 MB -> 175 MB -> 191 MB, not cumulative retention. Final uninstrumented 900.75-second natural drain passed 33/33 readiness samples while 538 background requests continued. Python RSS growth fell to only 4 KiB in the last five-minute/158-request window, file cache unchanged, no OOM/limit events. This is a bounded functional/memory PASS, not an indefinite-stability or all-provider-credentials claim

Authoritative final AC coverage, counts, slopes and conditional NAS deployment procedure: **logs/19-functional-memory-pass.md**. This final approval supersedes the historical holds below; PMA owns task closure and the separate NAS execution step. Unrelated maintenance findings and unavailable integration cases remain explicitly disclosed

## Retained-root correction pending final deployment

The slower retention now has a proven long-lived root: retry breadcrumbs retain live Logging objects, which retain exception tracebacks and completed Request bodies. Logging queues were empty; a one-frame allocation sample and direct field/traceback path establish the cause. Excluding only litellm_logging_obj from retry breadcrumbs passes two previously failing 25-request lifetime regressions and the 337-test focused matrix. See logs/18-retained-request-root.md for counts, diagnostic limitations and clock correction. Next exact-image repeated trials/drain/soak are pending; no NAS action or promotion PASS yet

## Latest JSON-contract verification and memory gate

Exact pushed source `2c6af6ee3aeeaa349f2169e37bfb383d7131e2ba` is deployed on Fedora as digest `e340ea66f58af527dfe56d7b229cc913163639497e03b7d9db154413116894c1`. The actual OpenAI SDK now receives Response objects for omitted/false stream, while true streaming remains functional. Real Chat, Responses, twenty repeated JSON calls and MCP/LazyMCP calls pass. 335 focused tests and direct checks pass

**API functionality PASS; promotion readiness HOLD.** Final-image 900.37-second availability/OOM observation passed all 91 samples, but another 927.74 seconds and later repeat sampling showed continued anonymous-memory growth to about 1.56 GB. The older image's mature plateau does not prove this final image has stabilized. No sustained-leak root cause or safe-to-promote memory claim is made. Fedora remains running with persistent 8-GiB/no-swap/restart=no containment; NAS remains unchanged

Detailed final client results, resource measurements, diagnostics and conditional NAS compatibility/deployment handoff: logs/17-json-live-memory-gate.md. The following sections are historical and must not override this latest hold

## Promotion-readiness continuation

The public Responses contract confirms stream=false must return a Response, although this fork's SSE behavior predates integration. A two-line sync/async correction keeps upstream ChatGPT SSE while using existing buffered parsing for non-stream callers. New text/tool/usage regressions and complete focused coverage pass: 335 tests, no skips. Mature-runtime memory comparison after about 2.5 hours stabilized near 1.33 GB; ten identical real calls caused no anon-memory growth, and recovery ended below pre-call current memory. Details and honest background-traffic accounting are in logs/16-stream-contract-memory-comparison.md. Rebuild/live SDK/900-second verification of this next checkpoint is pending; no NAS mutation is authorized

## Latest final observation

Fedora is running/healthy on exact registry digest `bc9a9123b774f5e2c250d2a9d4b5441397571e54cf41fc64c1192021940d6042`, built from pushed source `fb8943a9cc67573f34e0a56f6cb923f3a2dc845f`. Persistent 8-GiB/no-swap/restart=no containment survived recreation. Three product corrections are deployed: non-recursive ChatGPT session lookup, preserved account-profile parameters and Responses string-input normalization

232 focused isolated tests pass. Astra Chat streaming/non-streaming, Astra Responses SSE, Sol/Luna Chat, real LazyMCP defend_memory-find and standard MCP health invocation completed successfully. Final 900.36-second observation passed all 91 readiness checks, no OOM or memory-limit events, peak 1187172352 bytes. No rapid allocation burst recurred

**Not full release closure:** Responses stream=false still returns SSE under the existing explicitly tested provider-forced streaming contract; memory grew gradually by about 231 MB during the window; incoming Luna requests with temperature=0 and active reasoning continue to be rejected. The broad suite is not all-pass, and clean logs/indefinite memory stability/JSON non-stream semantics are not claimed. Route these contract/caller-policy questions through PMA. NAS remains untouched and promotion prohibited

Exact final source, digest, live matrix, sample series and AC coverage are in logs/15-final-fedora-observation.md. AC-1/AC-2/AC-3/AC-5 have the described evidence; AC-4 remains partial. The sections below are historical checkpoint records, superseded by this final observation

## First live correction result

Checkpoint 8865c5d20c75552d7db3a79f888c2c79f42fc02f was pushed, built and deployed by digest on Fedora. The allocation correction survived 900.37 seconds with all 91 readiness samples passing, zero OOM events and 1.17-GB sampled peak. Real Chat streaming/non-streaming and MCP/LazyMCP initialize/list passed. Direct Responses revealed the provider requires list input; the next minimal correction normalizes accepted string input in the ChatGPT provider. Three regression cases reproduce/fix it, and 232 focused isolated tests pass. See logs/14-first-corrected-live.md. Full functionality and final corrected-image soak remain pending; NAS remains untouched

## Tech Lead checkpoint review

PMA-authorized isolated comparison against unpatched HEAD classified the 15 broader failures without changing maintenance tools. Five cache-shape cases pass on both trees with inherited endpoints removed; one stale LazyMCP test expectation now includes the required `toolset_id=None`; nine external-provider failures reproduce with absent credentials and disabled networking on both trees. Focused product matrix: 229 passed, no skips. This does not turn the prior 964-pass/15-failure broad result into an all-pass claim

Both memory/profile source fixes are approved for the authorized product checkpoint, followed by exact clean-commit Dockerfile build and contained Fedora verification. No new image/live outcome is claimed at this checkpoint. Detailed classification and environment controls: logs/13-isolated-baseline-review.md. Maintenance findings remain untouched and NAS remains prohibited

## Latest Developer resume: auth propagation fixed, qualification blocked

PMA resumed exclusive Developer ownership after the Tech Lead diagnosis. Preserved the no-model_dump correction and all mapped regression tests. The three broader ChatGPT failures were caused by `get_litellm_params` omitting the already-forwarded `chatgpt_auth_profile`, `chatgpt_token_dir` and `chatgpt_auth_file` kwargs from sparse extraction. Added only those three strings to the existing optional-key set. No test assertions were weakened or altered

All ChatGPT tests plus mapped parameter-extraction tests pass: 115 passed, no skips, five existing multiprocessing deprecation warnings. The broader router/Responses/Chat-to-Responses run completed with 964 passed and 15 failed, with no skips and three built-in reruns. Six failures concern cache-injection/input shape and LazyMCP empty-map shape; nine concern provider credentials or unavailable integration models. These were not attributed to the two fixes and were not waived. Details are in `logs/06-router-responses-bounded-tests.log`

Important boundary correction: the broad router directory includes real-provider integration cases. Its inherited endpoint caused a speech test to reach the configured gateway and receive a model-unavailable response. This resume made no NAS deployment, service, configuration or database-administration changes, but cannot claim zero NAS endpoint traffic. Do not repeat provider integration tests under this inherited environment

Targeted Ruff passed. A raw strict basedpyright run reports existing-file diagnostics; the repository's actual basedpyright budget gate subsequently passed. Initial `make check` failed because host uv was too old. Rerunning with existing pinned uv 0.11.26 and frozen upstream baseline ed9d29a9b45d433db0c629bee9550f35980f00cb passed source Ruff, strict Ruff budget, type-discipline budget, basedpyright budget, E2E types and import checks, but failed two maintenance-test gates: RUF043 at test_disposable_runner.py:396 and TQ004 at candidate_secret_wrapper.py:23. No maintenance harness changes were made. StaticEng validation passed with zero warnings; diff whitespace validation passed

The five-path review diff is retained as `logs/11-source-review.patch`, SHA-256 `ab1dd2a25422d286c7bddd77a7271520a82dd6097cde510dfc95c16f5c351306`, against HEAD `2b3123c667b13ff0765ed6cc26d00eb6743d2458`. It includes both source corrections, the mapped Responses regressions, and two technical CodeMaps. Intended paths were temporarily staged for the canonical lint gate, then unstaged; no commit or push occurred

**Not build-ready or release-ready:** no corrected image was built, no dirty-source SHA was advertised as an image revision, no deployment or 900-second soak was attempted. The clean reviewed build contract requires TL checkpoint/approval, but the failed qualification gates must be resolved first. Fresh Fedora inspection confirms container c3f429b3da46f6595f0e9e9914f4053fc2ea2959b09b571ea7baf33a34ed33f8 remains exited, image b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3, restart count zero, memory and memory-plus-swap 8589934592, restart=no

AC-1 and the exact-caller evidence for AC-2 remain intact. AC-3 now has both minimal fixes locally and passing focused regression coverage, but broader qualification is blocked. AC-4 remains incomplete and Fedora unavailable. AC-5 includes current source hash and failed-check evidence. PMA must route the six assertion failures, approved provider-test environment and maintenance-gate findings without silently expanding this task into harness or cache-policy changes

Technical documentation was updated in `litellm/litellm_core_utils/codemap.yml` to record auth-profile propagation. No new product feature documentation is required; both changes restore intended existing behavior

## Latest Tech Lead diagnosis

The Python allocator caller is proven by two bounded live GDB captures: routed chat completion enters the Chat-to-Responses bridge, then ChatGPT Responses header validation calls session-ID extraction, which recursively serializes the entire GenericLiteLLMParams model. The local correction reads only the five session-related attributes. A 17-node shared synthetic graph consumed 24126536 peak traced bytes before the fix and 904 bytes after it. The live graph producer and request ID are not claimed

Changed source: `litellm/llms/chatgpt/common_utils.py`; mapped tests: `tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py`; technical invariant: `litellm/llms/chatgpt/codemap.yml`. Source at candidate revision and current HEAD had no differences under litellm before this patch. See `logs/02-tech-lead-python-caller.md` for exact stack, method, measurements and final identity

AC-1 remains satisfied by persistent containment. AC-2 has the exact allocating path and local amplification reproduction, but not payload provenance. AC-3 has a minimal local source patch and 33 passing Responses tests, not deployment qualification. Broader ChatGPT coverage has three auth-profile propagation failures independently reproduced without this patch. AC-4 remains FAIL/incomplete. AC-5 records this incomplete outcome. No failing test is waived

Final candidate container is `c3f429b3da46f6595f0e9e9914f4053fc2ea2959b09b571ea7baf33a34ed33f8`, same selected image digest as below, explicitly stopped after capture, restart count zero and final OOMKilled=false. Limits remain 8 GiB/no swap, restart=no. The earlier packet's container ID is historical. No corrected image was built/deployed and no commit, push, rollback or NAS mutation occurred

PMA should resume the original task for review and corrected-image verification, separately accounting for the three existing auth-profile failures. Product documentation is not required because no public behavior changes; the technical no-serialization invariant is recorded in the CodeMap. This task is not done or release-approved

## Summary

Persistent containment is repaired in Fedora's actual base Compose definition. The candidate remains selected but exited after three bounded cgroup OOM reproductions. This task is incomplete and is not a release PASS. No rollback, commit, push, dependency recreation, database mutation, or NAS deployment change occurred

## Work performed

The running object's Compose label named only `/home/staticduo/docker/litellm/docker-compose.yaml`, not the earlier optional containment overlay. Its base LiteLLM service had `restart: unless-stopped` and no memory limits. Applied `logs/fedora-containment.patch` on Fedora using `patch`, after a successful dry run. Only the first service's restart line changed, adding `mem_limit: 8g` and `memswap_limit: 8g`. Validated Compose and recreated only `litellm` using the exact base file with `up -d --no-deps --force-recreate litellm`

Verified effective memory.max=8589934592 and memory.swap.max=0 before probes. Docker restart policy is `no`. Subsequent manual starts retained containment and OOM did not cause an automatic restart

The recreated container is `35f034d9a9214e613df0b6add7bdbb046a448fef1367ad0923138b848415dabd`. Selected reference remains `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`. Docker reports that same digest as its local image ID. Image revision label is `bf58974a935521fa570fa7e280c51a00b2e5b54e`. No image was built or published. Repository HEAD at handoff was `2b3123c667`; existing unrelated worktree changes were preserved

## Acceptance criteria coverage

| Criterion | Result | Verification |
| --- | --- | --- |
| AC-1 | PASS | Base Compose corrected, config validation passed, actual recreation and effective cgroups verified; restart policy remained no after all three failures |
| AC-2 | PARTIAL | Three contained OOMs, event-loop starvation, bounded task counts and native stack captured. Defend find is not necessary to reproduce. Exact Python caller/request causality remains unproven |
| AC-3 | PARTIAL | Proven runtime containment correction applied. No speculative product source fix, retry changes or harness refactor. Product allocation fix remains blocked |
| AC-4 | FAIL | Readiness initially 200 and model inventory returned 29 aliases. Actual gpt-6-astra Responses returned HTTP 400. Candidate subsequently OOM-killed; no completed real-model/MCP matrix or soak |
| AC-5 | PASS for incomplete outcome | Exact runtime change, identities, measurements and blocker recorded here and in logs; task remains active for same-scope continuation |

## Findings

Second reproduction used only existing debug endpoints and cgroup samples from this operator, with unrelated live chat traffic present. No Defend call or nested embedding/rerank probe was sent. Memory remained roughly 904-946 MB with at most 24 sampled asyncio tasks. Immediately before growth there were 13 tasks, rather than a multiplying task population. The next sample reached 3064434688 bytes and both debug routes timed out, followed by exit 137/OOMKilled=true. This disproves the need for a diagnostic Defend call to trigger the failure, but does not exclude effects of other MCP or chat traffic

Third reproduction captured the main thread inside `_Py_dict_lookup`, `insertdict`, and repeated native `pydantic_core` frames while memory reached 1807577088 bytes. Other sampled threads were waiting. This narrows the growth phase to synchronous Pydantic/native dictionary work that blocks the event loop. It does not yet establish validation versus serialization, a particular model object, or the Python caller. See `logs/01-live-observations.md`

Bounded logs also show `UnsupportedParamsError` for gpt-5.6-luna and deployment-unavailable/rate-limit errors in chat routing. These are real availability failures, not proven causes of the native allocation burst. No retries were increased and no aliases or routing defaults were changed

## Documentation impact

This packet documents the operational truth: Fedora base Compose now disables automatic restart and caps LiteLLM at 8 GiB without swap. Preserve these settings on recreation while diagnosis continues. No product API or architecture change was implemented, so product documentation and source CodeMaps do not require changes. External Compose validation passed; no source/build change exists to run source regressions against

## Open risks and recommended next step

After three bounded failed runs, request Tech Lead assistance through PMA under the original task. Obtain the Python caller above the repeated native Pydantic frames, preferably with an already available compatible stack decoder, and correlate that caller with the triggering request or scheduled operation. Do not perform another blind restart or assume parameter normalization fixes the memory failure

Final state: candidate selected, container exited 137/OOMKilled=true, restart count 0, restart disabled, persistent 8-GiB/no-swap limits. Fedora is unavailable, NAS promotion remains prohibited. No new tool harness, instrumentation package, heap dump, raw payload or credential artifact was created
