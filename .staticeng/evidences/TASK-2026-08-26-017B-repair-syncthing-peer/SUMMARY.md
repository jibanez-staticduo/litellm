# TASK-2026-08-26-017B Evidence Summary

## Result

PASS. The authorized cachyos-only backup and supported Syncthing receive-only revert completed successfully

The single changed `AGENTS.md` was copied without reading or recording its contents to `/home/staticduo/.local/state/staticeng-backups/TASK-2026-08-26-017B-repair-syncthing-peer/AGENTS.md.pre-revert-20260826T133633Z`. The backup is outside both configured Syncthing folders, is owned by the effective user, has mode `0700`, preserves source size, nanosecond mtime, mode, UID, and GID, and remains present after repair

Syncthing's supported Revert Local Changes action was invoked for the exact receive-only OpenCode folder on cachyos. No NAS override, Syncthing configuration edit, restart, or unrelated host action occurred

## Acceptance Criteria

- **AC-1: PASS.** The backup path is outside every configured Syncthing folder. The regular-file backup is owner-only with mode `0700`, size 4,449 bytes, and preserved mtime `2026-08-22T07:29:28.855430+02:00`; source and backup size, mtime, mode, UID, and GID matched before revert
- **AC-2: PASS.** The approved Syncthing helper reported a successful peer-side receive-only revert for the exact folder. No configuration edit, NAS override, or restart was performed
- **AC-3: PASS.** Peer receive-only total, peer need total, peer need queue, needed bytes, and needed deletes are zero. NAS reports the peer at 100% with zero needed items, bytes, and deletes
- **AC-4: PASS.** NAS and peer are idle and unpaused with zero pull, folder, watch, or system-reported errors. Sequence exchange is aligned and conflict count is zero. A bounded peer scan completed; two snapshots three seconds apart were identical and converged
- **AC-5: PASS.** Evidence is metadata-only and secret-safe. The exact backup path and rollback warning are recorded

## Rollback Warning

Do not restore the backup automatically. Restoring `/home/staticduo/.local/state/staticeng-backups/TASK-2026-08-26-017B-repair-syncthing-peer/AGENTS.md.pre-revert-20260826T133633Z` into the synchronized folder would intentionally recreate the receive-only divergence and requires separate explicit authorization

## Safety

No shared file contents, device IDs, network addresses, credentials, content-derived hashes, prompts, or responses are present in this evidence

`staticeng_validate` remains blocked by the pre-existing repository-wide missing-CodeMap backlog. This task added no source directory or CodeMap obligation

See `logs/01-repair-and-verification.log` for the redacted operational record
