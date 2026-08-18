# NAS LiteLLM Staging Clone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove LiteLLM 1.98.0 on an isolated NAS clone before promoting it to production.

**Architecture:** A temporary Compose project runs LiteLLM, PostgreSQL, and Redis with independent names, storage, and a loopback-only port. It consumes copied production configuration and a restored database dump while global clients continue using production 1.92.0.

**Tech Stack:** Docker Compose, Bitnami PostgreSQL, Redis, LiteLLM 1.98.0, pytest, shell health probes

**Spec:** `docs/superpowers/specs/2026-08-18-nas-litellm-staging-clone-design.md`

## Global Constraints

- Do not change Fedora or the global OpenCode/Codex provider configuration.
- Do not expose staging outside `127.0.0.1:14000`.
- Do not print, commit, or copy secrets outside the staging runtime.
- Do not recreate production dependencies or restore the production database.
- Use image digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`.

---

### Task 1: Make the Legacy Runtime Patch Safe

**Files:**
- Modify: `/volume2/docker/litellm/patches/mcp_subject_token_optional.py`
- Modify: `/volume2/docker/litellm/tests/test_mcp_subject_token_optional.py`

**Interfaces:**
- Consumes: LiteLLM MCP manager source file
- Produces: `patch_file(path: Path) -> str` returning `not-needed:<path>` for fixed implementations

- [x] Add a regression test with an initialized `subject_token` call site.
- [x] Run the test and observe the old patch modifying valid code.
- [x] Scope detection to `_call_regular_mcp_tool` and return without modification when initialized.
- [x] Run the patch unit tests successfully.
- [ ] Execute all host patch tests and dry-run the patch sequence inside both 1.92.0 and 1.98.0 images.

### Task 2: Create the Isolated Staging Stack

**Files:**
- Create: `/volume2/docker/litellm-staging/docker-compose.yaml`
- Copy: production runtime configuration into `/volume2/docker/litellm-staging/`
- Create: `/volume2/docker/litellm-staging/postgresql-data/`
- Create: `/volume2/docker/litellm-staging/evidence/`

**Interfaces:**
- Consumes: production config/data, generated staging database password, immutable image digest
- Produces: Compose project `litellm-staging` with endpoint `http://127.0.0.1:14000`

- [ ] Capture production NAS and Fedora identities before staging.
- [ ] Copy operational configuration and data without release archives or database storage.
- [ ] Create a Compose file with unique container names, private PostgreSQL/Redis, and loopback-only LiteLLM port.
- [ ] Render Compose config with secrets redacted and verify no production container names or host ports conflict.

### Task 3: Clone and Restore PostgreSQL

**Files:**
- Create: `/volume2/docker/litellm-staging/evidence/production.pgdump`

**Interfaces:**
- Consumes: live production PostgreSQL database
- Produces: independent restored staging database

- [ ] Create a fresh custom-format dump without stopping production.
- [ ] Start only staging PostgreSQL and Redis.
- [ ] Restore the dump into staging PostgreSQL and verify schema/table counts.
- [ ] Record dump size and restore status without credentials.

### Task 4: Deploy and Validate LiteLLM Staging

**Files:**
- Create: `/volume2/docker/litellm-staging/evidence/staging-validation.txt`

**Interfaces:**
- Consumes: restored database and copied runtime configuration
- Produces: release decision for the immutable 1.98.0 image

- [ ] Start staging LiteLLM and wait conditionally for health.
- [ ] Verify image digest, version, restarts, OOM state, readiness, and liveliness.
- [ ] Compare authenticated staging inventory with the saved 40-model production baseline.
- [ ] Run a structured Responses unique-marker probe through a known-valid account.
- [ ] Run LazyMCP discovery and tool-call probes and inspect correlated logs.
- [ ] Review startup/runtime logs and recheck production NAS and Fedora identities.

### Task 5: Promote the Validated Candidate

**Files:**
- Modify: `/volume2/docker/litellm/.env`
- Preserve: `/volume2/docker/litellm/releases/20260818-2a8d1a6051/`

**Interfaces:**
- Consumes: staging pass evidence
- Produces: production NAS LiteLLM 1.98.0 on the same digest

- [ ] Back up the corrected patch and production selectors.
- [ ] Set production to the immutable candidate digest.
- [ ] Recreate only production `litellm` with `--no-deps`.
- [ ] Repeat health, inventory, Responses, LazyMCP, Codex, restart, OOM, and log gates.
- [ ] Move `main-latest` only after all production gates pass.
- [ ] Record release facts and remove staging only after final verification.
