# Reopen 1 NAS preflight and deployment

Fedora authorization: `.staticeng/evidences/TASK-2026-09-05-001-repair-fedora-runtime/logs/19-functional-memory-pass.md`

Actual host is NAS, Docker context default, explicit endpoint unix:///var/run/docker.sock, daemon ID 8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f, amd64, memory capacity 67162083328 bytes. Available memory before preparation was approximately 23 GB

Actual Compose project/service is litellm, source /volume2/docker/litellm/docker-compose.yaml. Fresh prior container 7bfb357accc8663e7229ecf8e2df471b9d656625106c216f48ca109de1eb2dba was healthy, restart 0, OOM false, on selector docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04 and config 0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42

Protected recovery directory: /volume2/docker/litellm/releases/TASK-2026-09-01-004-reopen1, mode 0700. Selector, Compose, config and wrappers copied, equality verified, mode 0600. Custom-format DB dump completed and pg_restore --list succeeded: 1543500646 bytes, SHA-256 1b7d0e2e6b88d7af1273899d3bd65d85dcc172131c4927172394ce124e1ba524. Mounted-state archive completed with exit 0, 6958438400 bytes. No production database restore performed. The first dump hit the command deadline and was replaced by the complete verified dump, not accepted as a backup

Schema preflight: 203 successful distinct migrations, three historical rolled-back entries, zero unresolved failures. Candidate has the same ten pending migrations reviewed in TASK-2026-09-03-003; migration/schema files unchanged between its reviewed source and final repair source. Startup reached 213 successful migrations, zero unresolved failures, same three historical rollbacks. This is schema preflight plus inherited isolated upgrade/startup-rollback evidence, not a fresh full-data restore rehearsal

Only .env LITELLM_IMAGE and LiteLLM Compose mem_limit=8g, memswap_limit=8g, restart=no changed. Exact rendered comparison proved every other LiteLLM setting, other service and top-level field unchanged; nonselector environment bytes match backup. This preserves NAS-specific configuration rather than copying Fedora configuration

Deployment command: docker --host unix:///var/run/docker.sock compose --project-directory /volume2/docker/litellm -f /volume2/docker/litellm/docker-compose.yaml --env-file /volume2/docker/litellm/.env up -d --no-deps --pull never litellm

Container 6b6f8743c69dab2a768dc76bef046511c7486bf0627d3fc0bc0a587bd4ff314c started 2026-09-05T13:49:53.305830462Z and reached healthy in the bounded startup poll. Memory.max=8589934592, memory.swap.max=0, restart 0, OOM false. Initial sampled memory.current=1224667136 bytes, all memory event counters zero

Baseline and post-deployment API inventory: 38 model aliases and 27 MCP registrations, exact model alias list preserved. Dependencies were not recreated: PostgreSQL fd90df4d0a7ee5fbefcf6e69985fb4cd2ce029abb1089e4802e46ab971bd4e07, Redis 3a9077b07d9dc1f08ce9170027cd91be6acc9d57ec03ed099fcd53b732095a05, admin MCP 9bfe616fad7506e3b5cef53559a835df14218568572dfef907e5da7b9e79e50f, compatibility MCP 0f58f7a2291f8900df937e54056cba2f9c68ddc47b13f88a6511aec738ab23fd

Registry identity is an OCI index, not a single manifest: authorized index 7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9 selects linux/amd64 manifest 9753f91ea752ddc7e01c03d282d8a059c08297e6ed66a9271744b89324415065 with config 02a12f580ddbaddc0e27529901d629fb54d4ec571257af7afe090f9decf4850f and 21 layers. NAS classic Docker reports this config as .Image; Fedora containerd reports the index as .Image. These are different engine identity representations, not different releases. Both revision labels equal 7a9ef0335303d973f3a228dcf7baadff18c82fb5
