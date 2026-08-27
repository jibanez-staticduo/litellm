# Release Verification

- Fix commit pushed to `origin/main`: `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`
- Branch disposition: no distinct matching local or origin feature branch exists
- Immutable image digest: `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`
- Image OCI revision exactly matches the fix commit
- Fedora previous digest: `sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c`
- NAS previous digest: `sha256:8a688990cb66fa7bd804fc8ac7423dd487dfd876d10fa7ef384096ab373ff6e5`
- Fedora final state: running, healthy, readiness 200, zero restarts, OOM false
- Fedora bounded log result: one expected redacted access line; zero raw marker, `Logging error`, and NoneType unpack matches
- NAS final state: running, healthy, readiness 200, zero restarts, OOM false
- NAS bounded log result: one expected redacted access line; zero raw marker, `Logging error`, and NoneType unpack matches
- LazyMCP final connected status: enabled, mode `lazymcp`, 27 visible servers, 535 visible tools
- Rollback required: no
