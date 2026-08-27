# AC-6 Predeployment Baseline And Rollback

- Captured before image build, registry push, Compose mutation, or container recreation
- Compose location: `/volume2/docker/litellm/docker-compose.yaml`
- Compose SHA-256: `cda96c4205cab8291505d0e8155fd3d962aa58c509bcd0bf307ba0f5843d029e`
- Config SHA-256: `95affd137dd1e5c5039063bd4ba7b29cff3417e646f22795575f81827dc3a8e4`
- Previous immutable image: `docker.staticduo.com/litellm@sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c`
- Previous local/running image ID: `sha256:53196f48d0aee0b610e6b884e1f16a13afea29ffa2a4bae29f13062758de9b21`
- Previous container state: running, healthy, zero restarts
- Compose and `.env` modes: `0600`
- Only the `litellm` service is authorized for recreation; unrelated services and persistent configuration must remain unchanged

Exact rollback command:

```bash
D=/volume2/docker/litellm
PREVIOUS=docker.staticduo.com/litellm@sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c
sed -i "s|^LITELLM_IMAGE=.*|LITELLM_IMAGE=${PREVIOUS}|" "$D/.env"
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" --env-file "$D/.env" pull litellm
docker compose --project-directory "$D" -f "$D/docker-compose.yaml" --env-file "$D/.env" up -d --no-deps litellm
```
