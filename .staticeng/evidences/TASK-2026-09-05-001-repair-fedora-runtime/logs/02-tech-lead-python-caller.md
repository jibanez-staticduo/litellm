# Python caller and minimal source correction

## Live evidence

Tech Lead took exclusive diagnosis ownership after the Developer handoff. All runtime commands targeted `ssh fedora`; no NAS runtime action, rollback, image build, commit or push occurred. Source comparison `git diff bf58974a935521fa570fa7e280c51a00b2e5b54e HEAD -- litellm` was empty

Fresh container identity was `c3f429b3da46f6595f0e9e9914f4053fc2ea2959b09b571ea7baf33a34ed33f8`, not the earlier identity in the Developer packet. Its image and selector both remain the approved `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`. Memory and memory-plus-swap were both 8589934592, restart policy no. The cause/timing of the earlier container replacement was not established

The installed Fedora GDB has usable CPython type information from loaded extensions even though libpython itself lacks debug types. No py-spy installation, custom harness, injected application code, heap dump or locals dump was needed. GDB ran with auto-load disabled, frame arguments suppressed, a ten-second deadline and explicit detach. Read-only decoding followed `_Py_tss_tstate`, `PyThreadState.current_frame`, `_PyInterpreterFrame.previous`, and the code object's filename/name/first line/instruction offset. Only code metadata and the parameter type name were printed

Preliminary attempts stopped once while idle because a human-readable memory-unit trigger matched the limit as well as usage. A subsequent sampler incorrectly reused the obsolete container ID and missed another contained OOM. Sampling was corrected to derive the current ID and read numeric memory.current, aborting on read failure. These attempts are not causal evidence

First successful allocation capture, PID 906687, measured 856485888 bytes at sample 10, 870817792 at sample 60, and 1803796480 at sample 70. The native stack had over 100 repeated pydantic_core frames. The current Python frames were `pydantic/main.py:model_dump` (function starts at 427) and `chatgpt/common_utils.py:_normalize_litellm_params` (257). The candidate was stopped after detach

Second successful allocation capture, PID 917283, measured 843939840 bytes at sample 20, 864489472 at sample 80, 871399424 at sample 100, then 1809457152 at capture. GDB stopped in native `dictresize`. The parameter type was `GenericLiteLLMParams`. The captured Python stack, innermost first, was:

```text
file                                                        function                            firstline byteoffset
pydantic/main.py                                            model_dump                          427       76
litellm/llms/chatgpt/common_utils.py                          _normalize_litellm_params            257       116
litellm/llms/chatgpt/common_utils.py                          get_chatgpt_session_id               275       14
litellm/llms/chatgpt/common_utils.py                          ensure_chatgpt_session_id            293       14
litellm/llms/chatgpt/responses/transformation.py              validate_environment                43        102
litellm/llms/custom_httpx/llm_http_handler.py                  async_response_api_handler          2783      320
litellm/responses/main.py                                    aresponses                          453       1346
litellm/utils.py                                             wrapper_async                       1750      2030
litellm/completion_extras/litellm_responses_transformation/handler.py acompletion                  305       426
litellm/main.py                                              _resolve_dispatched_chat_response    709       12
litellm/main.py                                              acompletion                         387       2114
litellm/utils.py                                             wrapper_async                       1750      2030
litellm/router.py                                            _acompletion                        3127      1272
litellm/router.py                                            make_call                           7367      170
```

This proves incoming routed chat processing through the Responses bridge is the active allocating path, rather than a background task or Defend invocation. No operator model/MCP request was sent in these captures. The upstream HTTP request has not yet been dispatched at this header-validation point. A particular request ID, input value, graph field and the producer of the expanding graph were not inspected or established. Retry history is a hypothesis, not a proven producer

## Source correction

`common_utils.py::_normalize_litellm_params` called `model_dump()` on the entire model just to find a session identifier. The new Pydantic branch reads only `litellm_session_id`, `session_id`, `metadata`, `litellm_trace_id` and `litellm_call_id` attributes, without serializing or copying their descendants. The existing dictionary path, precedence, string conversion, generated-ID fallback and non-Pydantic duck-typed compatibility paths remain unchanged

The patch is local only. It has not been built into or applied to the Fedora image. No claim of repaired availability or completed soak follows

## Bounded local reproduction

Using the existing Python 3.13 venv, build an acyclic shared graph with 17 unique dictionaries but exponentially many traversal paths, place it in GenericLiteLLMParams metadata, and call the real session helper. No provider credentials, network requests or production data are involved

```python
from litellm.types.router import GenericLiteLLMParams
from litellm.llms.chatgpt.common_utils import get_chatgpt_session_id
import time
import tracemalloc

graph = {"leaf": 0}
for _ in range(16):
    graph = {"left": graph, "right": graph}
params = GenericLiteLLMParams(
    litellm_session_id="synthetic-session", metadata={"history": graph}
)
tracemalloc.start()
start = time.perf_counter()
assert get_chatgpt_session_id(params) == "synthetic-session"
print(time.perf_counter() - start, tracemalloc.get_traced_memory()[1])
```

Observed original: 0.2499 seconds, 24126536 peak traced bytes. Patched: 0.000098 seconds, 904 peak traced bytes. This is a synthetic amplification reproduction, not a recovered live payload. Do not increase graph depth to reproduce host OOM

## Regression results

The mapped Responses test file now covers recursive metadata and existing session precedence for dict/model input, plus a nested model serializer spy proving unrelated state is never serialized for trace-ID, call-ID and absent-ID cases. Temporarily removing the new Pydantic branch made all three serializer-spy cases fail with one unexpected serializer invocation each. The branch was restored

`LITELLM_LOCAL_MODEL_COST_MAP=True .venv/bin/pytest -q tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py`: 33 passed, no skips

Broader `tests/test_litellm/llms/chatgpt`: 74 passed, 3 failed, no skips. The failures are pre-existing auth-profile propagation failures at chat test lines 93, 151 and 200. Running those tests after removing this correction reproduced all three failures. They remain blocking, not waived or repaired here. Five multiprocessing/fork deprecation warnings also occurred in authenticator coverage

StaticEng validation passed with zero warnings. A targeted Ruff check initially found one import-spacing issue, which was corrected. Final lint/diff results are in the verification log

## Final runtime state

Final read-back: container c3f429b3da46f6595f0e9e9914f4053fc2ea2959b09b571ea7baf33a34ed33f8, PID 0, exited, unhealthy, restart count 0, OOMKilled=false on the final explicitly stopped run. Memory/memory-plus-swap remain 8589934592 and restart=no. Candidate selection unchanged. Fedora remains unavailable and NAS promotion is prohibited
