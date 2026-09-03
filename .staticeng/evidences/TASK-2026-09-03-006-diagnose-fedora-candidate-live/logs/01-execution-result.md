# Fedora Live Diagnostic Execution Result

## Frozen Subjects

```text
candidate manifest: sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
candidate config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
candidate source: bf58974a935521fa570fa7e280c51a00b2e5b54e
rollback manifest: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
```

## Preflight

The owner-only host attempt is `/home/staticduo/docker/litellm/releases/TASK-2026-09-03-006-20260903T231759Z`. It retains the protected database dump and raw sampler output at mode `0600`; neither production data nor request/response payloads were copied into repository evidence

Fresh backup size was 202,548,429 bytes with a 417-line restore listing. Isolated restore passed 161 completed migrations, 81 public tables, zero task-artifact tables, and complete disposable-resource cleanup. Compose normalization proved that candidate rendering changed only `services.litellm.image`. The exact rollback script passed shell syntax validation before mutation

Fresh Cosign 3.1.3 verification passed the exact candidate signature plus SPDX, CycloneDX, and SLSA provenance v1 attestations against the retained StaticDuo public key. Fedora independently verified the candidate image ID, amd64 platform, and exact source label

## Watchdog And Deployment

Independent processes sampled candidate cgroup/process/host memory every second, liveness/readiness every two seconds, and PostgreSQL/Redis/Defend container state every five seconds. All samplers ran across the selector transition and automatic rollback

Candidate startup passed in 51 seconds with exact image/source identity, healthy readiness/liveliness, zero restart/OOM, and 161 migrations. The 112 candidate memory samples ranged from 33,992,704 to 1,482,137,600 bytes with no swap, memory pressure, dependency restart, dependency OOM, or kernel OOM

## Stop And Rollback

The execution stopped before an MCP request because the available protected Fedora client configuration contained a legacy API key rather than an exact-audience DCR bearer for `https://litellm.defend.tech/toolset/defend_memory/lazymcp`. Using that key would not satisfy the runbook's audience gate. A task-local client script also lacked an interpreter line and exited before its precheck, which caused the fail-closed automatic rollback unit to run. No candidate request, payload, credential expansion, or production patch occurred

Rollback restored the exact prior digest and preserved every non-image byte. Five-minute stability passed with a 1,410,453,504-byte peak and zero new kernel OOM events. Dependency identities/start times, protected files, inventory APIs, migrations, and health remained unchanged. Rollback MCP initialize returned 200, and one real `defend_memory-find` returned HTTP 200 with a JSON-RPC result and `isError=false` under concurrency one and a 75-second client deadline

## Classification

The historical incident remains `candidate source/resource`: the candidate process alone reached about 100.3 GiB anonymous RSS and was globally OOM-killed while the Defend services and data dependencies remained running. Healthcheck timing, DB/Redis pools, route/auth, and upstream restarts cannot explain that allocation. The exact candidate phase responsible remains unproven because this attempt correctly sent no request without the mandated exact-audience credential

The execution-specific blocker is `route/auth prerequisite`: a suitable protected exact-audience bearer was not available. That does not supersede the historical resource root cause; it prevents the bounded run needed to localize the allocation

## Correction Contract

No correction is authorized in this task. PMA should create a task that uses the existing DCR authorization-code flow to mint a short-lived bearer bound exactly to the toolset resource, stores it owner-only outside Syncthing and repository evidence, verifies wrong-resource rejection, and hands its file location to the Tech Lead. TASK-006 may then reopen with a new backup and the same watchdog thresholds. A reproduced candidate memory rise after upstream acceptance should create a separate LiteLLM source task and regression around the LazyMCP call path and reentrant embedding/rerank result retention
