# Task 6 Evidence: Compatibility, Release and Nightly

## Owned Deliverables

- Extension `compatibility/release_manifest.py` and packaged `release-manifest.json`.
- `scripts/check_staticduo_compatibility.py`, `scripts/staticduo_release.py`.
- `tests/extension/test_release_compatibility.py`, extension `COMPATIBILITY.md`.
- Live nightly `~/.local/share/litellm-nightly/prompt.md` appendix and
  `test_verify_runtime.py` prompt contract class. No production helper guard changed.

## Verification

From `/home/staticduo/.codex/worktrees/litellm-modular-b/litellm`:

- `PYTHONPATH=extensions/staticduo-litellm/src .venv/bin/python -m pytest tests/extension/test_release_compatibility.py -q --no-cov`: 25 passed.
- `.venv/bin/ruff check scripts/check_staticduo_compatibility.py scripts/staticduo_release.py extensions/staticduo-litellm/src/staticduo_litellm/compatibility/release_manifest.py tests/extension/test_release_compatibility.py`: passed.
- `basedpyright --pythonpath .venv/bin/python scripts/check_staticduo_compatibility.py scripts/staticduo_release.py extensions/staticduo-litellm/src/staticduo_litellm/compatibility/release_manifest.py`: zero errors/warnings.
- `.venv/bin/python scripts/check_type_discipline.py extensions/staticduo-litellm/src/staticduo_litellm/compatibility/release_manifest.py scripts/check_staticduo_compatibility.py scripts/staticduo_release.py`: no violations.
- `python3 ~/.local/share/litellm-nightly/test_verify_runtime.py`: 28 tests passed.
- `.venv/bin/python scripts/check_staticduo_compatibility.py --repo . --upstream-ref upstream/main`: passed against OAuth baseline/upstream 541e3ed5305a530ebef74d5684d3aca2632c1009, core 1.106.0, extension 0.1.0.
- `--runtime` intentionally rejects the development environment: core distribution
  metadata is not installed. This is not evidence of production runtime acceptance.

A test setup missing a JSON import failed, was corrected and rerun successfully.
The first strict type run reported six local Final-loop/type issues; these were
corrected and the affected check rerun with zero issues.

## Contract Coverage

Version/minor mismatch, provider raw-source drift and historical hash provenance,
missing adapters/data, signature and critical MCP/callback interface disappearance,
dependency mismatch, installed module absence, native ABI export/hash mismatch,
wheel version/data, catalog source/generated tampering and complete release receipt source/wheel/native binding are rejection tests. The companion
packaging owner adds direct `packaging>=24.0`; no packaging/lock files were edited
by Task 6. Nine critical core interfaces are recorded, not a generic full API hash.

## External Validation Remaining

After the parent freezes/commits the final candidate: build both wheels, UI and
native binary once; generate catalog and release receipt; verify actual packaged
data and run isolated non-editable runtime check in the image. Apply/verify expected
OCI labels and pin core/extension receipt in the registry image. Publish and verify
registry digest before deployment. Parent owns production Fedora QA, final main
publication and identical digest NAS promotion. No Docker build, remote mutation,
container deployment, main publication or push was performed by this task.

Shared Hindsight recall was attempted twice but the configured tool returned
unavailable. Context7 packaging specification and Kindly official Python metadata
documentation were consulted. No secrets were emitted or persisted.
