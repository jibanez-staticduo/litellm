# Pre-change Baseline and Backup

- Production Compose SHA-256: `0a84fde576264b85d07e5535f25255ceb0eb8d120a729e91c140b4e52b0e185b`
- Staging Compose SHA-256: `4a370f3e96337c73e37d783d758fcdbab7a486d5c78e3ce193ee58e44b41d43a`
- NPM host 62 generated config SHA-256: `f9294a477401d39db128eb03aa26e595d728cad8f7f5d02f06890d2b26dfb50b`
- NPM host 62 API upstream: `http://litellm:4000`, TLS certificate ID 1, forced SSL, HSTS, HTTP/2, WebSocket, 600-second timeouts, and 32k response buffers
- NPM Docker DNS for `litellm`: production `172.28.0.29` and staging `172.28.0.39`
- Production: healthy, zero restarts/OOM, manifest `f44690e5...3b42a`, revision `8589869e1c`, five mounts, `llm-net` plus `npm_npm-net`
- Staging: healthy, zero restarts/OOM, manifest `5ca639a1...2d167`, revision `e7991580d2`, six mounts, private staging network plus `llm-net` and `npm_npm-net`
- Public readiness and liveliness returned HTTP 200; staging loopback readiness and liveliness returned HTTP 200

Backup directory: `/volume2/docker/litellm/releases/20260819T153656Z-TASK-2026-08-19-056-upstream-collision`

The directory is mode 0700. Both Compose copies, NPM host 62 config, host ID, and `SHA256SUMS` are mode 0600. `sha256sum -c` passed for all three rollback files before mutation and again after verification
