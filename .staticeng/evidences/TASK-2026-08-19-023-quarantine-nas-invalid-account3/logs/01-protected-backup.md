# Protected Account3 Backup

## Scope

The pre-mutation inventory contained eight `chatgpt-account3/*` deployment rows and eight public fallback rules containing one account3 target each

The exact deployment IDs were:

- `84ed6a3c-0467-4e90-954b-692bff48572e`, `chatgpt-account3/gpt-5.3-codex`
- `b9a09c9b-988d-43a7-ac5a-59deae7328f9`, `chatgpt-account3/gpt-5.3-codex-spark`
- `e6795f7a-8e1d-43ca-ac59-244d3bbc04b7`, `chatgpt-account3/gpt-5.4`
- `e477d5bf-79bd-4163-8a7e-cc55b99994f7`, `chatgpt-account3/gpt-5.4-mini`
- `4982efb7-9d39-46db-8009-2e1c05b1f68c`, `chatgpt-account3/gpt-5.5`
- `02273e65-743e-403f-bbdc-8f2c78e6c3fe`, `chatgpt-account3/gpt-5.6-luna`
- `66f1d7dd-9f4d-4d06-a62b-b7e5fee16e32`, `chatgpt-account3/gpt-5.6-sol`
- `0948fb1e-1edc-4d56-a985-2f212cf54fc5`, `chatgpt-account3/gpt-5.6-terra`

Each public fallback chain contained account3 between or after its preserved default/account2 targets. The protected router-settings row records all eight exact pre-mutation chains and every unrelated router setting

## Protected Files

Backup directory: `/volume2/docker/litellm/releases/20260819-quarantine-account3/`, owner `0:0`, mode 0700

- `account3-deployments.sql`, mode 0600, SHA-256 `bc5585cb20310e7dcc4c9d79ea33a74a378aa92e9aad432127b0ab2686d25f0b`
- `router-settings.sql`, mode 0600, SHA-256 `90f902df423b6c2f2f30a24a8ad33a692ea7359b6ee803bc36dbaa452dc54ac0`
- `RESTORE.sql`, mode 0600, SHA-256 `91a02193269da9a2de95913c4af7e9e27cc40e8e16420966eedef79c097ffb82`
- `MANIFEST.json`, mode 0600, SHA-256 `e2987d7bd486c3fb266538c48d2c372c1d8c3ce3df44f17e1617ba8dd6944f03`
- `ROLLBACK.txt`, mode 0600, SHA-256 `d405de6c8865a5df95035a54bcc8e5821cd3c75128243da870346c9de0cd2c43`

The SQL files contain protected database values and were never printed or copied into repository evidence

## Exact Restoration

`RESTORE.sql` is one PostgreSQL transaction. It deletes only the eight account3 IDs to make restoration deterministic, reinserts their exact original rows, replaces only the `router_settings` row with its exact original value, and commits atomically

`ROLLBACK.txt` records the protected hash check, transaction command, same-image LiteLLM restart, and post-restore verification. The account3 credential and all historical credential backups remain untouched, but restored routing must not be enabled until user-assisted reauthorization succeeds

A transaction dry run replaced only the final `COMMIT` with `ROLLBACK`, executed all eight inserts plus the exact router-settings replacement successfully, and rolled back. Final quarantine state was then reverified

Result: **PASS**
