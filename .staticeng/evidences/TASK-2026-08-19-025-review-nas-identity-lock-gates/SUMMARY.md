# NAS Identity And Lock Gate Review

## Summary

The two reported failures are harness false positives. The immutable registry manifest digest and Docker image config digest identify different OCI objects and must not be compared to each other. The candidate is correctly identified by manifest digest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b` and config digest/image ID `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`

The drifting salted path is one of the three allowlisted zero-byte `<credential>.lock` synchronization files, not a credential file. On Linux, every token/account access opens that file, acquires an exclusive `flock`, and unconditionally calls `chmod(0600)`. The chmod updates ctime even when mode remains 0600, while ordinary lock acquisition does not require a content write. Recurring ctime-only drift with unchanged path, type, symlink state, owner, mode, size, mtime, inode, and device is therefore expected lock lifecycle behavior and does not require an OAuth refresh log

One controlled parent redeployment is **APPROVED**, subject to every corrected gate below and all unchanged parent stop/rollback rules. This approval does not approve stable promotion

## Work Performed

- Reviewed the task, parent task, approved SCR, complete parent evidence packet, candidate build identity evidence, prior OAuth disposition, auth hardening evidence, repository CodeMap, and the authenticator lock implementation
- Verified Docker's container inspect `Image` field is the image ID from which the container was created, while digest-pinned pulls and `RepoDigests` identify registry manifests
- Verified the Linux lock path is opened as `<auth_file>.lock`, chmodded to 0600, and exclusively locked with `fcntl.flock`
- Defined corrected identity and credential gates in `logs/01-gate-disposition.md`
- Performed no credential-content inspection and no host, registry, container, service, configuration, model, route, auth, or tag mutation

## Acceptance Criteria Coverage

- **AC-1: PASS**. Registry manifest and Docker config/image ID semantics are distinct and exact corrected assertions are specified
- **AC-2: PASS**. The path is an allowlisted regular zero-byte per-profile auth synchronization lock; ctime-only advance is expected from unconditional chmod during ordinary access
- **AC-3: PASS**. Parent evidence proves unchanged credential path set, type, symlink state, owner, mode, size, mtime, ctime, inode, and device, with zero correlated auth/device-flow failures. Credential contents were not read, but unchanged ctime and all other metadata establish that no credential-file write or content drift occurred during the observation. Non-empty credential files remained non-empty and mode 0600
- **AC-4: PASS**. Exact non-weakening gates are recorded and one controlled parent redeployment is approved conditionally

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. This investigation corrects a transient operational verification harness without changing application behavior or source

## Open Risks

- The candidate functional, 10-minute observation, Responses, Codex, LazyMCP, and cross-host gates remain unexecuted after the prior mandatory stop
- Stable remains unresolved exactly as inherited and is outside this redeployment approval
- Any non-lock credential metadata drift, any lock drift beyond ctime, or any auth/device-flow failure still requires rejection and rollback
- `staticeng_validate` remains blocked by pre-existing repository-wide broken links and missing CodeMaps. Repair dry-run proposed hundreds of unrelated generated maps and Markdown changes, so applying it would violate this investigation's atomic scope

## Recommended Next Step

PMA should reopen the parent task for exactly one controlled NAS redeployment from the verified rollback state, replacing only the two false-positive assertions with `logs/01-gate-disposition.md` and preserving every other parent stop and rollback rule
