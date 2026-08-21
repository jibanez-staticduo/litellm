# Release And Deployment

- Release source: clean detached worktree `/home/staticduo/git/litellm-release-task-20260821` at pushed product commit `eceb5129d3d29bd73bd446be2aa75d955f782d69`
- Safe overrides: `PRODUCTION_WORKDIR` set to clean worktree, `FORK_REMOTE=origin`, `UPSTREAM_REMOTE=upstream`, `--no-upstream-merge`, Fedora deployment disabled because this task targets the NAS runtime stack
- Image tag: `docker.staticduo.com/litellm:task-20260821-coordination-redis-eceb5129d3`
- Registry digest: `sha256:002358c594940dc7a78796062b3af2a11a48eb370531207d5059f8f61e71865d`
- Local image ID: `sha256:3c7d4e8e1a8d8ae7e6ca17eaee11655d66980cf402263199c1efe09026f8888d`
- Rollback tag: `docker.staticduo.com/litellm:rollback-task-20260821-coordination-redis-20260821-104623`
- Rollback digest: `sha256:7e6ef374b208271ca18f6d1985fbb4ea9df7bbb7335a52ca76f9cebd55f1e6c7`
- Runtime compose env is pinned to the immutable task tag
- Deployment result: LiteLLM healthy/running, Redis healthy/running, LiteLLM restart count 0
