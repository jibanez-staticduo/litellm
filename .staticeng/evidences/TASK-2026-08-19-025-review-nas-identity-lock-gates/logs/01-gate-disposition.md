# Corrected Identity And Credential Gates

## Classification Basis

The candidate uses two valid, intentionally distinct OCI identities:

- Registry manifest/deployment digest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Manifest `config.digest`, Docker image `.Id`, and running container `.Image`: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`

The manifest digest identifies the registry manifest selected by `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`. The config digest identifies the image configuration object and is the Docker image ID. Comparing running container `.Image` directly to the manifest digest is invalid

The salted lock path is an allowlisted `<auth_file>.lock` regular file. `Authenticator.get_access_token()` and `get_account_id()` open it with `a+`, set mode 0600, and acquire an exclusive cross-process `flock` on Linux. The unconditional chmod can advance ctime on every access despite no content, mtime, inode, owner, or mode change. The Linux lock file remains zero bytes because only the Windows fallback writes a lock byte

## Exact Corrected Image Identity Gate

Set these immutable expected values before deployment:

```text
CANDIDATE_REF=docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b
EXPECTED_MANIFEST=sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b
EXPECTED_CONFIG=sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73
```

Require all of the following independently:

1. Pull by `CANDIDATE_REF`, never by a mutable tag. Pull success must cryptographically validate the referenced registry manifest
2. The pulled image's `.RepoDigests` contains exactly `CANDIDATE_REF`
3. Registry manifest field `.config.digest` equals `EXPECTED_CONFIG`
4. Local `docker image inspect CANDIDATE_REF --format '{{.Id}}'` equals `EXPECTED_CONFIG`
5. Running `docker inspect CONTAINER --format '{{.Config.Image}}'` equals `CANDIDATE_REF`
6. Running `docker inspect CONTAINER --format '{{.Image}}'` equals `EXPECTED_CONFIG`
7. Package version remains 1.98.0, architecture remains linux/amd64, and OCI revision remains `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`

Reject if any assertion fails. Never assert `.Image == EXPECTED_MANIFEST`; those values identify different OCI objects

## Exact Corrected Credential Metadata Gate

Keep the existing T0 timing, complete salted-path allowlist, exact entry count, directory mode 0700, entry mode 0600, regular-file/non-symlink checks, owner checks, sanitized log cursor, and T1 checks immediately after readiness and after 10 minutes

Classify each pre-approved salted path before comparison as either a non-empty credential/historical file or one of the exact three approved zero-byte lock files. Do not classify a new path as a lock merely because it is empty

For every non-empty credential or historical file, preserve the existing strict rule: presence, type, symlink state, UID, GID, mode, size, mtime, ctime, inode, and device must equal T0 unless a credential replacement satisfies the existing positive OAuth-refresh HTTP 2xx exception. Failed refresh, device-code/login prompt, interactive-auth failure, provider-auth 401, invalid-file warning, auth-write failure, unexplained write, empty credential, path-set change, permission drift, or owner drift remains a mandatory rejection

For each exact allowlisted lock path, require presence, regular-file type, non-symlink state, identical UID/GID, mode 0600, size 0, identical mtime, identical inode, and identical device. Permit ctime to equal or advance from T0 without refresh correlation. Reject a ctime regression and reject any simultaneous change to another field. This exception applies only to the three pre-approved salted lock paths and never to a credential, historical file, directory, or newly observed path

No credential content may be read or retained. Lock ctime alone is not evidence of token rotation, successful refresh, failed refresh, or device authentication. Sanitized auth/device-flow log gates remain mandatory and independent

## Redeployment Decision

**APPROVE EXACTLY ONE CONTROLLED NAS REDEPLOYMENT**

Approval conditions:

1. Start from the exact healthy rollback state recorded by the parent evidence
2. Capture a fresh T0 within 60 seconds and pass the corrected identity and credential gates
3. Recreate only NAS `litellm` with `--no-deps` using `CANDIDATE_REF`
4. Preserve every other parent functional, topology, dependency, mount, network, protected-file, clean-log, cross-host, stop, and automatic rollback rule unchanged
5. Roll back NAS and restore the required cross-host state on any failure
6. Stop after this single attempt and return to PMA if any corrected gate fails

This approval is limited to redeployment verification. Stable/latest promotion remains prohibited until the parent acceptance matrix and independent cross-host QA pass
