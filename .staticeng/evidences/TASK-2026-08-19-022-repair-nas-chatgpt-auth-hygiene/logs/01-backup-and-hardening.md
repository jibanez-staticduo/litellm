# Backup And Permission Hardening

Captured at `2026-08-18T23:18Z` through `2026-08-18T23:36Z`

## Pre-Mutation Findings

- The configured token root remained `/app/data/chatgpt-auth`, with `auth.json`, `account2.json`, and `account3.json` as the three registered profile files
- The directory was a non-symlink directory owned by the NAS service user/group mapping and had mode `0777`
- All ten entries were regular non-symlink files; seven were non-empty credential or protected historical files and three were empty lock files
- Two protected revoked default-profile files had legacy mode `0777`; the remaining entries had mode `0600`
- Credential contents were not emitted, retained in command output, or written to evidence

## Protected Backup

- Backup path: `/volume2/docker/litellm/releases/20260819-chatgpt-auth-hygiene/original/`
- The parent and copied auth directory are owned by `0:0` with mode `0700`
- All ten copied entries are owned by `0:0`, regular, non-symlink, and mode `0600`
- The backup was completed and verified before the live permission mutation

## Live Hardening

- `/volume2/docker/litellm/data/chatgpt-auth` is now owned by `0:0`, non-symlink, and mode `0700`
- All ten entries are now owned by `0:0`, regular, non-symlink, and mode `0600`
- Seven non-empty files remain non-empty; three approved lock files remain empty
- No profile was removed or renamed

Result: **PASS** for backup, type, symlink, ownership, and permission hardening
