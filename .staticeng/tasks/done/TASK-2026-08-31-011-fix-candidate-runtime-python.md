---
id: TASK-2026-08-31-011-fix-candidate-runtime-python
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Fix candidate runtime interpreter validation

## Objective

Determine and govern the smallest Dockerfile correction for the final runtime validation using system `python` instead of the copied `/app/.venv` interpreter, while preserving image startup/runtime behavior and production.

## Acceptance Criteria

- [x] AC-1: Identify exact failing Dockerfile command, current runtime PATH/VIRTUAL_ENV/entrypoint contract, and why system Python is selected.
- [x] AC-2: Determine whether the correct fix is explicit `/app/.venv/bin/python`, runtime `ENV`, PATH ordering, or another existing repository convention.
- [x] AC-3: Recommend the smallest fail-closed correction and tests proving Prisma, uvloop, LiteLLM Rust bridge, interpreter ABI, and normal image entrypoint use the intended venv.
- [x] AC-4: Document exact Dockerfile scope, manifest/checksum impact, compatibility risks, and rollback.
- [x] AC-5: Update task with signed evidence; do not mutate Dockerfile/source/images/production/deployment.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-006 Reopen 2 evidence and inspect root Dockerfile final stage, entrypoint, production image environment, alternate Dockerfiles, and CI conventions. Prefer an explicit validation interpreter if runtime already intentionally relies on another startup mechanism; do not silently change runtime PATH without proving compatibility. Research only, update this task, and return an exact recommendation for Tech Lead.

# Post Implementation Task Updates

## Technical Architect: Post Investigation Expectations

### Summary

PASS for investigation. Reopen 2 exposed two linked defects, not a missing runtime `PATH`. The runtime already prepends `/app/.venv/bin`, and `prod_entrypoint.sh` intentionally resolves `litellm` through that path. The builder nevertheless downloaded managed CPython 3.13.13 for `.venv` after APK installed pinned CPython 3.13.15. The copied venv therefore does not have a usable runtime-local interpreter contract. Shell lookup skips its unusable `python` and reaches system `/usr/bin/python`, which cannot see venv site-packages. Changing only the assertion to `/app/.venv/bin/python` would fail earlier rather than repair the image. The smallest fail-closed correction binds both syncs to `/usr/bin/python3.13` and makes the final assertion invoke `/app/.venv/bin/python` explicitly

### Work Performed

- Read TASK-006 Reopen 2 summary and logs. The exact failure is root `Dockerfile:164`: `python -c "from prisma.client import BINARY_PATHS; ..."` exits with `ModuleNotFoundError: No module named 'prisma'`, while the immediately preceding builder output records generation at `/app/.venv/lib/python3.13/site-packages/prisma`
- Traced the stronger precursor in the same immutable build log: APK installed `python-3.13=3.13.15-r4`, but the first `uv sync --python python3.13` downloaded and selected managed CPython 3.13.13 before creating `.venv`. The build therefore did not satisfy the intended 3.13.15 interpreter/ABI gate even before the final assertion
- Inspected the final stage contract. Root `Dockerfile:133` already persists `PATH=/app/.venv/bin:<base PATH>`; `VIRTUAL_ENV` is unset; `ENTRYPOINT ["docker/prod_entrypoint.sh"]` executes either `litellm` or `ddtrace-run litellm` by PATH. `docker/entrypoint.sh` separately prefers the explicit venv interpreter for migrations. The production image and running container also preserve venv-first PATH and resolve `python`, `python3`, and `litellm` from `/app/.venv/bin`; no production mutation was performed
- Compared maintained image conventions. `docker/Dockerfile.database`, `docker/Dockerfile.non_root`, `backend/Dockerfile`, and `gateway/Dockerfile` all use venv-first runtime PATH and bare validation `python`; the current production venv points to system `/usr/bin/python3`. These conventions work only when the builder venv is based on the runtime-available system interpreter. None establishes `VIRTUAL_ENV`, and none justifies changing PATH order
- Checked current uv guidance. uv may download a managed interpreter when selection does not bind a usable system interpreter; `--no-managed-python`/`UV_PYTHON_DOWNLOADS=never` can prohibit that fallback, and an absolute `--python` path binds venv creation to that interpreter. On Unix the resulting venv executable links to the selected base interpreter, so the builder/runtime package pin must remain identical

### Options Considered

1. **Bind both syncs to `/usr/bin/python3.13` and explicitly validate with `/app/.venv/bin/python`: RECOMMEND.** This repairs the copied venv's interpreter provenance, preserves the established runtime PATH/entrypoint contract, and makes the build assertion independently fail if the venv executable is missing or unusable
2. **Change only `python -c` to `/app/.venv/bin/python -c`: REJECT.** Reopen 2 proves uv created the venv with downloaded CPython 3.13.13 rather than pinned system CPython 3.13.15. An explicit invocation is a useful assertion but cannot make that copied managed interpreter available or satisfy the pinned ABI contract
3. **Add or reorder runtime PATH: REJECT.** The required venv-first order is already present and inherited by later `RUN`, `ENTRYPOINT`, and containers. Rewriting it is behaviorally broader and cannot repair an unusable executable at its first entry
4. **Set `VIRTUAL_ENV=/app/.venv`: REJECT.** Python does not use `VIRTUAL_ENV` to discover site-packages, and the console scripts already carry venv shebangs. Adding it changes observable runtime environment without repairing interpreter provenance
5. **Use only `UV_PYTHON_DOWNLOADS=never` or `--no-managed-python`: NOT PREFERRED.** Either blocks fallback, but an absolute interpreter path is narrower and directly couples both syncs to the exact APK-installed executable. A global environment switch affects all later uv commands and is unnecessary once both existing selectors are explicit

### Exact Minimal Recommendation

Tech Lead should authorize only these three substitutions in root `Dockerfile`; do not change runtime `ENV`, `VIRTUAL_ENV`, entrypoints, package pins, locks, source, alternate Dockerfiles, or deployment:

```diff
-    --python python3.13
+    --python /usr/bin/python3.13
```

Apply that substitution to both existing `uv sync` commands at current `Dockerfile:94` and `Dockerfile:115`

```diff
-    python -c "from prisma.client import BINARY_PATHS; paths = list(BINARY_PATHS.query_engine.values()); assert paths and all(p.startswith('/opt/prisma/') for p in paths), paths"
+    /app/.venv/bin/python -c "from prisma.client import BINARY_PATHS; paths = list(BINARY_PATHS.query_engine.values()); assert paths and all(p.startswith('/opt/prisma/') for p in paths), paths"
```

Apply the assertion substitution at current `Dockerfile:164`. This is the minimum correction because the first two changes establish a runtime-portable venv from the pinned interpreter and the third prevents PATH fallback from ever masking a broken venv again

### Required Verification

1. Re-freeze the eight-path candidate manifest with only root `Dockerfile` fingerprint and combined patch checksum changed; prove `pyproject.toml`, `uv.lock`, Cargo files, six application paths, base digests, Rust OCI provenance, and parser checksum are unchanged
2. Build `linux/amd64` with the prior `--pull=false` contract. Build output must show system CPython 3.13.15 selected and must not show a managed CPython download. Both frozen syncs, Maturin bridge build, Prisma generation, and the explicit final assertion must pass
3. In the final image, run `/app/.venv/bin/python` directly and assert `sys.executable == '/app/.venv/bin/python'`, `sys.prefix == '/app/.venv'`, `sys.base_prefix == '/usr'`, Python `3.13.15`, expected `cpython-313` SOABI for the target architecture, and that `/app/.venv/bin/python` resolves through the installed runtime `/usr/bin/python3.13`
4. With an intentionally minimal PATH that still includes system utilities, invoke `/app/.venv/bin/python` and import `prisma`, `uvloop`, `litellm`, and `litellm.rust_bridge._native`; assert `uvloop.__version__ == '0.21.0'`, Prisma query-engine paths are nonempty and under `/opt/prisma`, and the native bridge loader reports availability
5. Inspect final image config for unchanged venv-first PATH, absent `VIRTUAL_ENV`, unchanged `ENTRYPOINT`/`CMD`, and unchanged Prisma environment. Run the normal entrypoint, not an overridden Python command, in TASK-006's isolated secret-free container and complete readiness, discovery, MCP, reconnect, preservation, and production-invariant smoke

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact failing command, generated Prisma location, downloaded builder interpreter, runtime PATH, absent `VIRTUAL_ENV`, and entrypoint resolution contract are traced
- **AC-2: PASS.** PATH and entrypoint are already correct. Explicit validation is necessary but insufficient alone; binding venv creation to `/usr/bin/python3.13` is the missing correction
- **AC-3: PASS.** Three exact substitutions and fail-closed build/image/entrypoint tests cover Prisma, uvloop, LiteLLM Rust bridge, interpreter version/SOABI, and normal startup
- **AC-4: PASS.** Scope is root `Dockerfile` only. Manifest, checksum, compatibility, and inverse rollback requirements are recorded
- **AC-5: PASS.** Only this governed task was updated. Dockerfiles, source, images, locks, production, configuration, databases, and deployment were not changed

### Documentation Impact

No product or steady-state architecture documentation is required. This correction restores the existing image contract rather than changing an interface or runtime behavior. No CodeMap changes are required because no source/module structure or verification command is added

### Open Risks

The complete corrected image has not been built, so venv symlink shape, native-extension loading, Prisma engine resolution, and startup remain TASK-006 gates. Builder and runtime must continue installing the exact same Python package/version; changing either side can make the copied venv non-portable. The correction intentionally does not solve broader live Wolfi APK-index reproducibility. Arm64 remains unauthorized until native arm64 verification. `staticeng_validate` is not required for this task-only research update and the known repository-wide missing-CodeMap inventory remains outside scope

### Rollback

Rollback is the inverse three substitutions and restoration of the previously frozen root `Dockerfile` fingerprint and candidate manifest/checksum. There is no data, configuration, image, container, or deployment rollback because this task authorizes no build promotion or production change. If either build-time interpreter provenance or final-image gates fail, reject the candidate and retain production unchanged

### Recommended Next Step

PMA should route a bounded root-Dockerfile implementation and independent Tech Lead review. Freeze a replacement eight-path manifest and combined patch checksum, then reopen TASK-006 from its existing scope for the full amd64 build and smoke contract. Do not authorize PATH, `VIRTUAL_ENV`, entrypoint, alternate-Dockerfile, lockfile, or production changes

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Reopen 2 is not a missing-PATH defect: runtime already uses venv-first PATH, but uv downloaded CPython 3.13.13 after APK installed pinned 3.13.15, leaving the copied venv without its intended runtime-local base. Authorize only both `--python /usr/bin/python3.13` substitutions plus explicit `/app/.venv/bin/python` for the Prisma assertion. Re-freeze the Dockerfile manifest/checksums and rerun all TASK-006 amd64 ABI, native-import, entrypoint, protocol, and production-invariant gates. Production remains unchanged

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-011 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
