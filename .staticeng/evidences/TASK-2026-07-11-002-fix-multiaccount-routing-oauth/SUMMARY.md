# TASK-2026-07-11-002 Evidence

## Result

Implemented isolated fallback attempts, immutable logical routing metadata, fail-closed ChatGPT cross-profile fallback without a request bypass, per-auth-path process and file-lock single-flight, and atomic owner-only auth writes

Final reopen additionally validates ChatGPT profile homogeneity before deployment selection, overwrites caller-supplied identity at the public router boundary, preserves identity only through a private fallback marker, and serializes account-ID merging under the same advisory lock

## Acceptance Criteria Mapping

- AC-1 and AC-2: default/no-profile is an explicit `default` identity; default/account2, reverse, mixed, and unresolved ChatGPT transitions fail closed
- AC-3 and AC-4: fallback attempts carry `original_requested_model`, `logical_model_group`, current `model_group`, fallback source, reason, and attempt without mutating caller data
- AC-5 and AC-6: stable resolved auth paths key reentrant process locks and Linux advisory file locks; auth files use same-directory temporary files, file and directory fsync, mode 0600, and atomic replace
- AC-7: focused identity, policy, concurrency, profile isolation, and atomic-write regressions were added
- AC-8: structured fallback logs contain requested/logical/current groups, attempt, source, and exception class; no request content or credentials are logged
- AC-9: project `uv` environment resolved dependencies; authoritative final results are 49 focused tests and 38 mapped tests passing, with warnings documented below
- AC-10: this packet contains the pre-fix regression, post-fix command results, and AC mapping; no live credentials or provider calls were used

## Verification

- Focused suite: 49 passed, with 5 Python 3.12 multiprocessing `fork` deprecation warnings on Linux
- Mapped suite: 38 passed, with 4 existing async resource warnings
- `uv run ruff format --check`: passed
- `uv run ruff check`: passed
- `git diff --check` passed
- Initial system-Python test attempt lacked `openai`; project `uv` was then used successfully without lockfile changes

## Pre-fix Regression

Before the fix, `run_async_fallback` reused and mutated `kwargs`, nested `metadata`, `model`, and `fallback_depth` across attempts. `Authenticator` checked cooldown outside any lock and wrote auth JSON directly to its final path

## Residual Risk

Cross-process locking uses conditional POSIX `fcntl` or Windows `msvcrt`; directory fsync runs only where `O_DIRECTORY` exists; temporary-file permissions use `fchmod` where available and path-based `chmod` otherwise. Multiprocessing uses `spawn` on Windows and `fork` on POSIX. The synchronous provider transformation path remains synchronous; no native async authenticator API was introduced

Token-directory hardening applies mode 0700 only to directories created by the authenticator. Existing configured directories retain their original permissions
