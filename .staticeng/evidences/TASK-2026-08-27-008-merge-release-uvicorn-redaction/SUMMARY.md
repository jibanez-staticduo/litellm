# TASK-2026-08-27-008 Evidence Summary

## Result

The reviewed Uvicorn access-log redaction fix is committed on `origin/main`, represented by one immutable image built from that exact commit, and deployed by digest to Fedora and NAS. Both hosts pass health, readiness, LazyMCP, redacted-access, and bounded clean-log gates

## Release Identity

- Source and fix commit: `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`
- Immutable image: `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`
- Built local image ID: `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`
- OCI revision: `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`
- Fedora running image identity: `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`
- NAS running image ID: `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`

## Rollback References

- Fedora previous digest: `docker.staticduo.com/litellm@sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c`
- NAS previous digest: `docker.staticduo.com/litellm@sha256:8a688990cb66fa7bd804fc8ac7423dd487dfd876d10fa7ef384096ab373ff6e5`
- Rollback method: restore the host's previous `LITELLM_IMAGE`, pull it, and recreate only `litellm` with `docker compose up -d --no-deps litellm`
- Rollback was not required

## Acceptance Criteria

- AC-1: PASS. The scoped fix commit contains only the authorized source, test, Task 023 closure/evidence, registry hunks, and Task 008 initial state. It is pushed to `origin/main`
- AC-2: PASS. Local and remote branch searches found no separate Uvicorn, redaction, or Task 023 feature branch. No branch deletion was required
- AC-3: PASS. One image was built from an isolated clean worktree at the pushed main commit, published with matching OCI revision, and deployed by the same immutable digest to Fedora and NAS. Both rollback digests were captured before mutation
- AC-4: PASS. Both hosts are running and healthy with zero restarts and OOM false; readiness returns HTTP 200. LazyMCP reports enabled mode with 27 visible servers and 535 visible tools. Each host's unique non-sensitive probe returned HTTP 401, emitted one `GET /lazymcp?REDACTED HTTP/1.1` access record, and left zero raw marker, `Logging error`, or `cannot unpack non-iterable NoneType object` matches in its bounded post-start log window
- AC-5: PASS. This packet identifies commit, digest, running image identities, rollback digests, host verification, branch disposition, and documentation impact

## Verification

- `.venv/bin/python -m pytest tests/test_litellm/test_secret_redaction.py -q`: 43 passed
- Changed-file Ruff lint and format checks: passed
- `git diff --check` for changed source and tests: passed
- Fedora: healthy, readiness HTTP 200, redacted probe PASS, bounded clean-log counts all zero
- NAS: healthy, readiness HTTP 200, redacted probe PASS, bounded clean-log counts all zero
- Connected LazyMCP status after both deployments: enabled, mode `lazymcp`, 27 visible servers, 535 visible tools
- `staticeng_validate`: see `logs/staticeng-validate.log`

## Documentation Impact

Product, architecture, technical, and CodeMap documentation updates are not required. The change corrects internal logging compatibility without changing routes, request behavior, configuration, or public contracts

## Security

Evidence records only aggregate marker counts and redacted access behavior. Raw unique markers, response bodies, credentials, and private configuration are not retained
