# Baseline And Rollback

## Source Baseline

- Branch: `main`
- Base revision: `b3f60643b8a1f9d5becc2b39f15f67f7638c5375`
- Reviewed runtime patch SHA-256: `ffef2b5158f997fb030a04ab796ee4384af95ee36c529daddfa44b40da277783`
- Stable patch ID: `01a15b1ad873b272c4c7bfa662672de5900c2aa5`
- The clean build context came from `git archive HEAD`; only the five reviewed runtime source files were applied. Tests and unrelated dirty files were not copied into the image build context by the patch
- Runtime file SHA-256 values matched between the reviewed worktree and clean build context:
  - `litellm/llms/base_llm/chat/transformation.py`: `4a8f678f98c9d7f84ed84afa882d1e3ea16f2e8dd186c60574b183208e114415`
  - `litellm/llms/base_llm/responses/transformation.py`: `46fe9a5e96bd47ecc01fd04247b590744341deb321ecc988f29b2c7fab84d511`
  - `litellm/llms/custom_httpx/llm_http_handler.py`: `47c0a06a26cfdb9ce64ba3ddc17a7836b2a679de7a7d692d04df768bf6143085`
  - `litellm/llms/hosted_vllm/chat/transformation.py`: `ca3fb43761837549af459f92a50065eaad8d46bd0f2010f674db90c821c79ab2`
  - `litellm/llms/hosted_vllm/responses/transformation.py`: `f432f1d488e3b53fc5bf47093bf6c38fb977c7e4cbb931a09a0fc80e5144b3b5`

## Protected NAS Baseline

- Production Compose SHA-256: `cda96c4205cab8291505d0e8155fd3d962aa58c509bcd0bf307ba0f5843d029e`
- Production config SHA-256: `bb2eb16811e76053f94fec1f42fd09d63b1f325e736802622f62aa2ca8ee39f2`
- Production image: `docker.staticduo.com/litellm@sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c`
- Production state: running, healthy, zero restarts, OOM false
- Staging Compose SHA-256: `5d6a6b030ed2272cf96ec5ff562eee1c52c9f28afd69e79c8a925264f0a14600`
- Staging config SHA-256: `d10d989072e329a3a47c11ee734783a08c8607865fa8e8fa940851e75f624272`
- Prior staging image: `docker.staticduo.com/litellm@sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Prior staging state: exited, zero restarts, OOM false
- Staging PostgreSQL identity: `25a7ab4c0c4a03acb24e0f44eb73277f82057f0a0b3eb989e16696048e0c339a`, started `2026-08-18T17:40:28.960555723Z`, healthy, zero restarts
- Staging Redis identity: `e69e7ef095b0dadb0be8e30a6da086e99ebcd9913cd20d4e6cb8d69e8457d72e`, started `2026-08-18T17:45:45.144943296Z`, healthy, zero restarts
- Production and staging `.env` files remained mode `0600`; only checksums and key names were inspected, never values

## Backup And Exact Rollback

- Owner-only backup: `/volume2/docker/litellm-staging/evidence/20260825T114521Z-TASK-2026-08-25-007`
- Backup directory mode: `0700`; backup Compose and checksum manifest mode: `0600`
- Exact rollback commands, with the database password obtained transiently from the already-running staging database container and never printed:

```bash
D=/volume2/docker/litellm-staging
B=/volume2/docker/litellm-staging/evidence/20260825T114521Z-TASK-2026-08-25-007
DBP=$(docker inspect litellm-staging-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | while IFS= read -r line; do case "$line" in POSTGRESQL_PASSWORD=*) printf '%s' "${line#*=}"; break;; esac; done)
export STAGING_DB_PASSWORD="$DBP"
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" stop litellm
cp "$B/docker-compose.yaml.before" "$D/docker-compose.yaml"
chmod 600 "$D/docker-compose.yaml"
sha256sum -c "$B/SHA256SUMS"
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" config --quiet
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" up -d --no-deps litellm
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" stop litellm
unset DBP STAGING_DB_PASSWORD
```

- Rollback executed successfully. Final staging Compose/config checksums match baseline, the prior image is restored, and `litellm-staging` is exited with zero restarts and OOM false
