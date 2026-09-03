# Read-Only Verification Ledger

## Repository

```text
HEAD 9374aae27c93d509a12f167c6bb1f83815ed3db1
HEAD parent 0573332425de92ad8f17f6eb3196fce0d3ce7f22
current Dockerfile sha256 e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11
proposed Dockerfile sha256 9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d
TASK-014 commit Dockerfile sha256 9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d
proposed versus TASK-014 Dockerfile diff: empty
current versus proposed semantic diff: exactly lines 4 and 7
```

Current dependency fingerprints are recorded only as a comparison baseline and must be recomputed by implementation:

```text
a65b83b54f2ae160ac7ffa06119588ac79ff5b08f7eda89e901f60063ff63bbb  pyproject.toml
2cbab3eb78c04cc8a8a7daa58550c7522071d9e39d2063917a52b79dc5635c12  uv.lock
6b5408b318905ec6cb37b6cea04b9aa95a664bea184bd8f492afa62775df18ab  litellm-rust/Cargo.toml
a9bbd9b2123c6aae1420aaf35fb79a5aa0be6bf782c4260110f7b5122342c05b  litellm-rust/Cargo.lock
```

## OCI Resolution

Read-only Buildx registry resolution returned:

```text
current Wolfi index sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72
current Wolfi linux/amd64 child sha256:52604323e2a19f5e6d37dffa7e6a7ef30e2f98506a73a11cdfa3ef25100131be
current Wolfi linux/arm64 child sha256:aa58277d1dc347a73505212255a6e51729d6cc4d1500321e011893edb9ee42d8

replacement Wolfi index sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
replacement Wolfi linux/amd64 child sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd
replacement Wolfi linux/amd64 config sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140
replacement Wolfi linux/arm64 child sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e

uv index sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a
uv linux/amd64 child sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8
uv linux/arm64 child sha256:40edad71a1710a9d5d988c6a034304e9c414d7f794dab44a0781d619bba41d33

Rust index sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3
Rust linux/amd64 child sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b
Rust linux/arm64/v8 child sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d

UI index sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43
UI linux/amd64 child sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43
UI linux/arm64/v8 child sha256:0e6f1567e269207c28295276928277a030139cbc5a0fb7d5bd2674f0401a9082
```

## Prior Compatibility Evidence

TASK-011 Reopen 2 selected Python 3.13.15-r4 on the current Wolfi base and failed because `math.cpython-313-x86_64-linux-gnu.so` requires `GLIBC_2.44`. Its build-base-only diagnostic substitution to the replacement digest completed the builder target

TASK-014 independently proved the replacement amd64 base contains glibc/loader 2.44-r1 and runs all four Python 3.13.15-r4 packages with `import math`, x86_64, `cpython-313`, and SOABI `cpython-313-x86_64-linux-gnu`

TASK-006 Reopen 4 built a full amd64 candidate from the TASK-014 Dockerfile and proved final Python 3.13.15, `/usr/bin/python3.13`-linked venv, glibc 2.44-r1, uvloop 0.21.0, Prisma, Rust bridge, representative native imports, unchanged entrypoint/CMD, and normal startup/readiness. Later Reopen 6 passed the packaging and isolated smoke contract for its exact source. These prior images are compatibility evidence only, not qualification of current source

## External Documentation

Official Chainguard package-model documentation reviewed on 2026-09-03 states that public Wolfi/Extra repositories retain non-latest package versions for a bounded period, remove eligible versions periodically, and advise users pinning old versions to mirror them internally

Official Chainguard verification documentation states that images and attestations are separately signed and must be verified with Cosign against the expected issuer and certificate identity. Exact image digest, platform, signature, provenance, and SBOM attestation verification are separate gates

Sources:

```text
https://edu.chainguard.dev/chainguard/containers/features/packages/package-model/
https://edu.chainguard.dev/chainguard/containers/how-to-use/verifying-chainguard-images-and-metadata-signatures-with-cosign/
```

## Mutation Boundary

No Dockerfile, source, test, lock, Cargo, alternate Dockerfile, image, container, builder, cache, registry, Git ref, host, database, production, deployment, or CodeMap mutation was performed. Only this task and its evidence packet were written
