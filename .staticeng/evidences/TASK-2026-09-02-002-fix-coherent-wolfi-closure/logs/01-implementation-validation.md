# Implementation And Validation Ledger

## Source And Exact Edit

```text
source commit: 9374aae27c93d509a12f167c6bb1f83815ed3db1
pre-edit Dockerfile sha256: e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11
post-edit Dockerfile sha256: 9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d
Dockerfile diff: exactly 2 removals and 2 additions at lines 4 and 7
non-StaticEng source paths changed: Dockerfile only
git diff --check: PASS
Dockerfile patch sha256: 269cab0cc2d24322b3b542dc27c10b884cc593c6b5972ba2169056e1287b0a38
```

Preserved dependency and toolchain inputs:

```text
a65b83b54f2ae160ac7ffa06119588ac79ff5b08f7eda89e901f60063ff63bbb  pyproject.toml
2cbab3eb78c04cc8a8a7daa58550c7522071d9e39d2063917a52b79dc5635c12  uv.lock
6b5408b318905ec6cb37b6cea04b9aa95a664bea184bd8f492afa62775df18ab  litellm-rust/Cargo.toml
a9bbd9b2123c6aae1420aaf35fb79a5aa0be6bf782c4260110f7b5122342c05b  litellm-rust/Cargo.lock
```

Rollback is the reversal of exactly the two substitutions and reproduces the pre-edit Dockerfile fingerprint above

## OCI Identity Resolution

Immediate read-only index resolution before build returned:

```text
Wolfi index: sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
Wolfi linux/amd64 child: sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd
Wolfi linux/arm64 child, metadata only: sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e
uv linux/amd64 child: sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8
Rust linux/amd64 child: sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b
UI linux/amd64 child: sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43
```

No build-argument override was used. Both effective Wolfi `FROM` inputs resolved from the committed replacement index. No arm64 execution occurred

## Native ABI Preflight

A disposable native `linux/amd64` base probe selected:

```text
glibc-2.44-2.44-r1
glibc-2.44-locale-posix-2.44-r1
ld-linux-2.44-2.44-r1
python-3.13-3.13.15-r4
python-3.13-base-3.13.15-r4
python-3.13-base-dev-3.13.15-r4
python-3.13-dev-3.13.15-r4
```

Python reported `3.13.15`, `x86_64`, cache tag `cpython-313`, SOABI `cpython-313-x86_64-linux-gnu`, and imported `math`. The loader reported `glibc-2.44-r1`, and `readelf --version-info` showed `GLIBC_2.44` in the math extension

## Clean Detached Builder And Final Builds

Docker Buildx `v0.32.1` used a uniquely named Docker-container builder running BuildKit `v0.13.1`. Both targets were built for `linux/amd64` with `--no-cache`, `--pull=false`, source revision label `9374aae27c93d509a12f167c6bb1f83815ed3db1`, and task label `TASK-2026-09-02-002`

```text
builder config/image ID: sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb
builder exported manifest: sha256:cfbbd3002425c510b3b4efef4e1bb4a8de5249422397f3d1f5a932dcbf3c80ac
final config/image ID: sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45
final exported manifest: sha256:71dac661d00ecf05693932ea88011625acc5e9500b53bdc7bcc0e7c5c455f12b
architecture: amd64
source revision labels: exact
task labels: exact
```

Both frozen uv syncs selected `/usr/bin/python3.13`. The clean builds completed the exact Rust identity assertions, Maturin bridge build, UI build, Prisma generation, copied runtime environment, and final Prisma engine assertion

## Builder And Final Runtime Gates

Builder evidence:

```text
installed APK packages: 68
embedded APK SPDX documents: 68
Rust release: 1.97.1
Rust commit: 8bab26f4f68e0e26f0bb7960be334d5b520ea452
Rust host: x86_64-unknown-linux-gnu
LLVM: 22.1.6
Cargo: 1.97.1
Python: 3.13.15
SOABI: cpython-313-x86_64-linux-gnu
```

Final evidence:

```text
installed APK packages: 48
embedded APK SPDX documents: 48
glibc loader: 2.44-r1
Python: 3.13.15
executable: /app/.venv/bin/python
venv prefix: /app/.venv
base prefix: /usr
venv executable realpath: /usr/bin/python3.13
architecture: x86_64
SOABI: cpython-313-x86_64-linux-gnu
uvloop: 0.21.0
Prisma query-engine paths: 4, all under /opt/prisma
native imports: aiohttp, cryptography Rust, grpc, LiteLLM, Rust bridge, NumPy, Prisma, pydantic-core, uvloop PASS
copied ELF interpreter resolution: PASS
PATH first entry: /app/.venv/bin
VIRTUAL_ENV: absent
ENTRYPOINT: ["docker/prod_entrypoint.sh"]
CMD: ["--port","4000"]
normal startup/readiness: HTTP 200
clean shutdown: exit 0, OOM false
```

## Security And Reproducibility Boundary

The APK transaction selected exact package versions shown by the clean build and package manifests. Embedded package SPDX documents were inspected by count. Public APK index and artifact retention remains mutable and bounded, so this evidence proves the executed transaction but does not establish future binary-identical rebuilds

Cosign, Syft, Grype, Trivy, and Docker Scout are unavailable. The apparent `docker sbom` command is not installed; invoking it routes to base Docker help. Therefore signature/attestation verification, aggregate builder/final SBOMs, same-database comparative scans, and Critical/High disposition remain blocked promotion gates and are not reported as passing

## Cleanup And Production Invariant

The disposable runtime container, ABI probe, builder image, final image, BuildKit builder/container and cache, and detached worktree were removed. Post-cleanup label checks found zero task containers, networks, volumes, and images. The worktree list contains only the repository root, and only the pre-existing default builder remains

Production was observed only with the two allowlisted formats. Its container identity, image, running/healthy state, restart count `0`, and OOM state `false` were identical before and after validation. No production `.Config`, Compose, environment, config, credentials, mounts, database, network, or host state was read or mutated. No Fedora, NAS, registry publication, deployment, commit, or push occurred

## Static Validation

```text
staticeng_validate: PASS
all source directories indexed
hierarchy validated
warnings: 0
```
