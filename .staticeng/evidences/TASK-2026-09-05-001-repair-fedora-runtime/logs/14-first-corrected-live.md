# First corrected image and real Responses defect

Product checkpoint `8865c5d20c75552d7db3a79f888c2c79f42fc02f` committed and non-force pushed to origin/main. Unrelated maintenance changes remained unstaged

Built on Fedora directly from `git archive` of that exact commit using the unchanged repository Dockerfile, linux/amd64. The first build used an abbreviated revision label and was not deployed. A cached rebuild corrected the label to the full SHA. Final image index/registry digest: `sha256:849c75ee0eef2855b79277886db2794d5b98182a6dcc426b8ed55f79b44efff9`, image config `sha256:3a75c66e41db44fca8d1417ffa6ceee9f25290d5c1c6bb0f30974c887c842d44`, amd64 manifest `sha256:1b27d0f016ef752070473ed7319c09a131f01f9dccb04faac13ac2176a19bf5d`. Registry candidate tag `task0905-8865c5d20c`. Isolated network-disabled image imports and both product checks passed

Build completed Python/Rust package installation, UI production build/typecheck and Prisma generation. Existing warnings included AVIF optimization support, Prisma Wolfi fallback and a Tornado test-directory removal message. No security or build-tool refactor was made

Applied only the retained selector patch to Fedora .env, validated the base Compose file, and recreated only litellm with --no-deps. Container `2d484f373c97f4f5a5b409a08ac20c2b0bd10b2fe3485bdb3d3d468c123701af` used the exact digest. Effective memory.max=8589934592, memory.swap.max=0, restart=no. No rollback or NAS service/configuration action occurred

Authenticated /v1/models returned 200 and 29 aliases. With model gpt-6-astra, harmless input `Reply with OK only` and low reasoning:

| Route | Stream | HTTP | Time | Result |
| --- | --- | --- | --- | --- |
| /v1/chat/completions | false | 200 | 3.052s | OK present |
| /v1/chat/completions | true | 200 | 2.160s | OK and DONE present |
| /v1/responses | false | 400 | 0.628s | upstream rejects string input |
| /v1/responses | true | 400 | 0.836s | upstream rejects string input |

Sanitized provider detail: `Input must be a list`. This is a real product defect in native ChatGPT Responses input normalization, separate from the allocation failure. The bridge already supplies list input, explaining successful Chat Completions

## 900-second observation on this image

91 samples over 900.37 seconds, readiness 200 on every sample, no cgroup max/oom/oom_kill events. Initial memory.current 962539520, final 1157001216, sampled peak 1172393984 bytes. The former rapid multi-GiB native allocation burst did not recur. Slow growth of about 194 MB across the window remains an observation, not proof of a flat long-term heap

MCP /mcp and /lazymcp initialize/list both returned 200; initialized notifications returned 202. Standard MCP listed 147 tools; LazyMCP listed exactly mcp_describe, mcp_call and mcp_status. Real read-only invocation and final corrected-image matrix remain pending

## Minimal next product correction

ChatGPT Responses request transformation now converts string input to a one-item user input_text list, preserving list input. Three mapped cases cover normal string, empty string and existing list. Before correction: two string cases failed, list case passed. After correction: focused isolated matrix 232 passed, no skips, four existing multiprocessing warnings; direct source/test Ruff passed

No upstream parameter-policy change, retry change, alias change, maintenance-tool change or security refactor was made. The task remains active and this image is not full-function qualified because direct Responses failed. Rebuild the next exact checkpoint and repeat the live matrix plus 900-second observation before NAS consideration
