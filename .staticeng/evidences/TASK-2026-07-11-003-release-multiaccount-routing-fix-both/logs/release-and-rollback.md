# Release and rollback

```text
source_commit=8dcccc5cd201d777aee23e3004242e73d8ed4207
image_tag=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-multiaccount-routingfix-20260711
registry_digest=sha256:ca28db906704c63afc9b73bd40a201edadb10da30e214542fcada54748dd2497
previous_image=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708
previous_digest=sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316
local_rollback=docker.staticduo.com/litellm:rollback-multiaccount-routingfix-local-20260711
fedora_rollback=docker.staticduo.com/litellm:rollback-multiaccount-routingfix-fedora-20260711
```

The image was built from a clean detached worktree. The existing release script was used in build-only mode with the repository's actual `origin` and `upstream` remote names. Deployment then used each instance's existing Compose stack without model or credential mutation.
