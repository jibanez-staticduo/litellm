# Runtime bootstrap correction

PMA explicitly authorized a minimal backed-up correction to the real mounted startup wrappers, preserving the new candidate selection and actual host-specific functionality. This supersedes the startup hold in log 05; no rollback, Frigate repair, credential change or tool framework work occurred

## Exact cause and decision

Fedora's /home/staticduo/docker/litellm/start-litellm.sh checked for psql and ran `apk add --no-cache postgresql-client` when absent. Its PostgreSQL client was used only to wait for the DB and repeatedly add the legacy source_url column. A separate Python block corrected synthetic Responses health input, followed by a background LiteLLM process and waits

The candidate does not contain psql. Read-only Prisma queries against each actual database returned one existing public.LiteLLM_MCPServerTable.source_url column. The column also exists in the maintained schema. The missing client therefore does not justify a runtime package install for this obsolete schema repair. Ordinary application startup/migration behavior remains responsible for database connection/schema readiness

The stalled apk process was sleeping in poll_schedule_timeout.constprop.0 with no interactive TTY. The official Wolfi index was reachable, so a generic network outage was not established. No claim is made about which package download/version/repository wait held apk; removing its now-unnecessary caller eliminated the startup dependency without changing package repositories or installing tools

Fedora correction removes the legacy psql install, DB wait, DDL-repair loop and child waits. Its existing guarded Responses health-check correction is preserved byte-for-byte. The wrapper now ends with `exec /app/docker/prod_entrypoint.sh "$@"`. Shell syntax passes, and the same candidate listened after a bounded poll of 10 seconds

NAS was inspected independently. Its wrapper contained only the PostgreSQL install/column-repair/background-process code, with no health patch. After its own schema check and backup, it was reduced to the shell preamble and the same exec. NAS did not inherit Fedora's health override. It listened after a bounded poll of 25 seconds following promotion

## Persistent paths and recovery

Fedora Compose root: /home/staticduo/docker/litellm

NAS Compose root: /volume2/docker/litellm

Each actual docker-compose.yaml still mounts that host's start-litellm.sh as /app/start-litellm.sh. Each wrapper invokes the image's existing prod_entrypoint.sh with unchanged arguments. Both .env selectors use the exact 4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258 digest

Both roots retain owner-only releases/TASK-2026-09-05-002-residuals backups of .env, docker-compose.yaml, config.yaml and the original wrapper. Existing earlier database/mounted-state recovery was not removed or overwritten. No database restore or manual DDL was performed. The initial NAS unprivileged backup attempt failed before mutation; the supported local sudo path then made the protected backup and applied the root-owned configuration change

Fresh final comparisons passed on both hosts: original nonselector environment bytes unchanged, Compose/config.yaml byte-equal to backups, and original wrapper backup present. Only the selector and the intended wrapper logic differ. NAS's 38 model deployments and 27 MCP registrations retain identical before/after alias and server-ID digests

Model alias digest: 270eeccde701257a79263573c72286bcd083b77c81c141c5b9f7f1187392ae5e

MCP server-ID digest: 585c32047496d167746e0fb0646b900f388be01f47fe39f92d6c4b4b7e808158

All four NAS dependency container IDs from the preceding deployment remain the same and running with zero restarts/OOM. Both host recreations used their actual Compose paths, --no-deps and --pull never; Fedora's wrapper correction additionally forced recreation of only LiteLLM

## Versioned configuration snapshots

The secret-free final wrapper snapshots in ../config are byte-identical to the live host wrappers, verified by SHA-256. The .txt suffix marks evidence snapshots, not a new executable framework

Fedora: 4f62fbc87dc6a304bae910482b49c2f0aa33de0317f88e622ae5d15000176cc0

NAS: 15a1d5207f5a36b5961ba922532fc5fbbe9584d70480e746f53fcf0b2ca4935c

Both snapshots pass `sh -n`. The inherited Fedora health patch still changes its two installed health-check files at startup; sharing the image digest does not imply those host-overridden runtime files are byte-identical to NAS. No new application source change or image rebuild was needed for this configuration correction
