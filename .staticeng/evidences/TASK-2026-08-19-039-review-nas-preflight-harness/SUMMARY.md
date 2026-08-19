# NAS Preflight Harness Review

## Summary

The current parent harness is rejected as written because it omits the empty-directory protected mount gate and relies on the `fedora` SSH alias without an explicit remote identity assertion. One corrected parent attempt is approved after the developer incorporates every fail-closed gate below and validates the corrected shell syntax. This approval permits one parent deployment attempt, not a weakened preflight or additional probe traffic

## Work Performed

- Read the child and parent tasks, approved SCR, parent harness, and relevant prior NAS/Fedora deployment evidence
- Inspected NAS path and Docker mount metadata without reading credential contents
- Resolved `fedora` with `ssh -G` and performed one metadata-only isolation check against the literal endpoint as `staticduo`
- Made no runtime, credential, service, configuration, registry, or remote mutation and sent no inference, health, auth, or application request

## Exact Corrected Gates

### AC-1: Protected directory metadata/hash gate

Treat `/volume2/docker/litellm/data/op_service_account_token` as a protected empty directory, not a regular file. Fail closed unless `lstat` proves a non-symlink directory owned by `0:0`, mode `0755`, with an empty direct-child set. Capture a canonical baseline containing type, uid, gid, mode, size, mtime_ns, ctime_ns, inode, device, and the SHA-256 of the sorted direct-child metadata projection. Require byte-identical baseline/final projections

Also require the Docker mount tuple to remain exactly `/volume2/docker/litellm/data/op_service_account_token|/run/secrets/op_service_account_token|bind|false` before and after. Continue SHA-256 checks for the four protected regular files: Compose, config, startup wrapper, and OnePassword wrapper. Reject a symlink, regular-file substitution, non-empty directory, ownership/mode drift, mount-source/destination/type/RW drift, or protected-file hash drift

### AC-2: Credential directory discovery

Use only these literal approved host roots and their corresponding container locations:

- `/volume2/docker/litellm/data/chatgpt-auth` and `/app/data/chatgpt-auth`
- `/volume2/docker/litellm/data/anthropic-auth` and `/app/data/anthropic-auth`

Do not glob for credential directories, recurse under `/volume2/docker/litellm/data`, or inspect similarly named backup paths. For each literal host root, fail closed unless `lstat` proves a non-symlink directory, `realpath` equals the literal path, ownership is `0:0`, and mode is `0700`. Inspect only direct children. Every child must be a non-symlink regular file owned by `0:0` with mode `0600`. Persist only a SHA-256 label of each basename plus category/type/uid/gid/mode/size/mtime_ns/ctime_ns/inode/device, never file contents or content hashes

Require the baseline and final key sets to be identical. For non-empty credential files, require every metadata field to remain identical. For zero-byte lock files, require every field except ctime_ns to remain identical and allow ctime_ns only to stay equal or advance. Any new/deleted path, token mtime/size/inode/device drift, lock regression, symlink, special file, ownership change, or mode change rejects and rolls back

### AC-3: Fedora isolation

Do not rely on an unqualified SSH alias. Use `staticduo@fedora-ssh.staticduo.com`, which the local SSH configuration resolves for `fedora`, with `BatchMode=yes`, `RequestTTY=no`, `StrictHostKeyChecking=yes`, and forwarding disabled. The remote command must first require `id -un` to equal `staticduo` and `id -u` to equal `1000`, then perform only Docker metadata inspection without `sudo`

Capture container ID, image identity, state, health, restart count, OOM flag, start time, exact mount source/destination/type/RW tuples, and exact network name/ID tuples before the NAS attempt. Require byte-identical output afterward and require the image identity to equal the approved replacement identity. Any SSH identity, host-key, command, image, container, state, mount, or network mismatch rejects and rolls back NAS

## Acceptance Criteria Coverage

- **AC-1: PASS**. The protected service-account source was verified as a root-owned empty `0755` directory mounted read-only by bind, and the exact fail-closed baseline/final gate is defined above
- **AC-2: PASS**. The two approved literal roots were verified as root-owned `0700` directories containing only direct root-owned `0600` regular files, without reading contents
- **AC-3: PASS**. `ssh -G fedora` resolved user `staticduo` and literal endpoint `fedora-ssh.staticduo.com`; the live metadata-only check asserted `staticduo`, uid 1000, and a healthy unchanged Fedora container on the replacement identity
- **AC-4: PASS**. Reject the current script as written. Approve exactly one corrected parent attempt after all three corrections above are incorporated and `bash -n` passes

## Documentation Impact

No product or architecture documentation update is required. This investigation refines a one-use operational harness under the already approved SCR

## Open Risks

- The current parent script still lacks these corrections at review time
- The approved retry remains fail-closed and must not proceed if the corrected preflight cannot establish every predicate
- Repository-wide CodeMap coverage is absent, consistent with previously disclosed StaticEng validation debt

## Verification

- Targeted `git diff --check`: PASS
- Current parent `bash -n`: PASS before the required semantic corrections
- `staticeng_validate`: FAIL on inherited broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps
- `staticeng_repair` dry run: reviewed but not applied because it proposes hundreds of broad unrelated Markdown and CodeMap changes

## Recommended Next Step

PMA should return the exact gates to the assigned developer. The developer may incorporate them, run `bash -n`, and execute one corrected parent attempt. Any further correction or retry requires a new PMA disposition
