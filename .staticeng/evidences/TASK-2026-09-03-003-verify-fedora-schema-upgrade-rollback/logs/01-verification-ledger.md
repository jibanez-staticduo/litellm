# Secret-Safe Verification Ledger

## Safety Boundary

```text
Fedora commands: read-only pg_dump, psql SELECT/COPY TO STDOUT, docker inspect
captured application rows: 0
captured environment/configuration: 0
captured credential values or URLs: 0
production mounts or networks attached: 0
host ports published: 0
deployment/restart/config/DB mutation/publication/sign/NAS action: 0
```

The source fixture was owner-only mode `0600`, reviewed before restore, used only under `/tmp/opencode`, never placed in repository evidence, and destroyed after the test

## Fedora Preflight

```text
LiteLLM container: b02395bd50ba36faa05a6a7182307f47a1cdc0f2d69fe6a71fd0515b55b43dd0
selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
runtime: running, healthy, restart 0, OOM false
started: 2026-09-03T04:53:42.90650887Z
PostgreSQL: 17.11
extensions: plpgsql only
ledger state: 151 successful | 0 unfinished | 0 rolled back | 151 total | 151 distinct | 0 with logs
ledger SHA-256: dbe062506165bb0babb7ad3f3e2ae59769bd7aef194ce38c57c07d12e5f67c11
normalized schema SHA-256: 3840c0c0d05065c08b1d12237ca002bd77fe9b39c336f966f0dbd783d738c9ce
```

Raw PostgreSQL 17 dumps include randomized `\\restrict` tokens, so normalized schema checksums exclude only the generated `\\restrict` and `\\unrestrict` lines

## Fixture Review And Restore

```text
artifact mode: 0600
artifact bytes: 146242
artifact SHA-256: 60dbf300397c9f98bafe992e886e1dd32a3abac07dcbbe0644d00beecda7504a
schema tables: 73
application COPY statements: 0
application INSERT statements: 0
ledger rows: 151
credential URL markers: 0
restored ledger: 151 successful | 151 total | 151 distinct | 0 with logs
```

Disposable resources used the exact label `staticeng.task=TASK-2026-09-03-003`: container `task003-schema-db`, network `task003-schema-net`, volume `task003-schema-vol`, candidate `task003-schema-candidate`, and rollback `task003-schema-rollback`. PostgreSQL used local image config `sha256:d741b376874687de90374fd34f55c6b2760e8f7bd7e4ae5cd47f50757fc08cf8`

## Migration Identity

```text
candidate migration count: 161
candidate migration-set SHA-256: bd39ff9ecca85da8b82685f00532c6c22e87b8907003917e4074f1544fe9273f
rollback migration count: 151
rollback migration-set SHA-256: eba7f17da315150f9cd4d3dcd57c8beca4d85ae32af69f8513206141aa48bbfb
pending migration count: 10
pending migration-set SHA-256: 81fdcd2be453adffadf09429c4782a446612a806328fbe6cea05dfe6ed40eb4c
```

The exact pending names were compared transiently against the candidate application result. Evidence retains only their set checksum and count

## Candidate Upgrade And Restart

```text
image config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
first start: running, healthy, restart 0, OOM false
post-upgrade ledger: 161 successful | 0 unfinished | 0 rolled back | 161 total | 161 distinct | 0 with logs
exact pending set applied: 10 of 10
normalized schema SHA-256: 0caa0590706e5a4f94c0b4152166db3f04ae4d282c689de9a7de7be5b54f6be9
ledger SHA-256: 3acc73bbecec0c70978a1a05fce5352a40317fb035d6cddaaf8a313aeff10fa2
idempotent restarts: 2 of 2 healthy
restart schema checksum change: none
restart ledger checksum change: none
```

Sanitized candidate log classification:

```text
first-start log stdout SHA-256: d1605ead2fb3cb4d75b3a1c7ac157ab5ae21c54fd1bb9b09504343b18df51301
first-start log stderr SHA-256: 17e034523771b1e200811e2a14e3dee854591832a8a58e650e7f9e61988ceaf8
restart log stdout SHA-256: 5c7eaf8a01ac73df1c1fa7c84fd31bb4bd67ef1d30e07ebf5dba5cab8bef470f
restart log stderr SHA-256: 2a5dacacb85c58a21ec0e277deeed53b62a1f837b9b9de0b6cc44daf9ee25ef1
traceback: 0
migration failure/error: 0
HTTP 500 marker: 0
unknown migration warning: 0
first-start applying-migration lines: 10
first-start successful migration completion: yes
restart no-pending classification: yes
```

Raw logs were inspected locally, reduced to checksums/status/classifications, and destroyed

## Rollback Compatibility

```text
registry selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
image config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
runtime: running, healthy, restart 0, OOM false
packaged migrations: 151
upgraded ledger visible: 161 successful | 0 unfinished | 0 rolled back | 161 total | 161 distinct | 0 with logs
startup classification: no pending migrations
normalized schema before/after: 0caa0590706e5a4f94c0b4152166db3f04ae4d282c689de9a7de7be5b54f6be9
ledger before/after: 3acc73bbecec0c70978a1a05fce5352a40317fb035d6cddaaf8a313aeff10fa2
```

Sanitized rollback log classification:

```text
stdout SHA-256: f9ef9cc0cb27bb17911b29de20e7b4492dd753490086d74758472b4124d60d01
stderr SHA-256: 49f852f470ea7cdc9eed67f2d94097656838c07f026d9d07e904188eccdcc047
traceback: 0
migration failure/error: 0
HTTP 500 marker: 0
unknown migration warning: 0
no-pending classification: yes
destructive/reverse migration observed: no
```

## Cleanup And Fedora Postflight

```text
task-labelled containers: 0
task-labelled networks: 0
task-labelled volumes: 0
owned temporary runtime/schema artifacts: 0
Fedora LiteLLM identity/start time changed: no
Fedora state: running, healthy, restart 0, OOM false
Fedora ledger state: 151 successful | 0 unfinished | 0 rolled back | 151 total | 151 distinct | 0 with logs
Fedora ledger SHA-256: dbe062506165bb0babb7ad3f3e2ae59769bd7aef194ce38c57c07d12e5f67c11
Fedora normalized schema SHA-256 pre/post: 3840c0c0d05065c08b1d12237ca002bd77fe9b39c336f966f0dbd783d738c9ce
staticeng_validate: PASS, 0 warnings
```

Result: PASS for AC-1 through AC-6
