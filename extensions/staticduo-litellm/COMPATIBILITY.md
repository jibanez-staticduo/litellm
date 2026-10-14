# Compatibility and Release Contract

`compatibility/release-manifest.json` is packaged with the extension. It defines
extension version, supported core versions, reviewed upstream OAuth provenance,
critical callback/MCP/OAuth signatures, required data/modules and Rust exports.
Wheel checks bind the complete Python/JSON inventory and exact file bytes to the
reviewed candidate; installed runtime checks hash every corresponding file.
`release_manifest.py` validates frozen Pydantic contracts; it does not patch core.

## Source Gate

Run before merging freshly fetched upstream, then again against the final commit:

```sh
python scripts/check_staticduo_compatibility.py --repo . --upstream-ref upstream/main
python scripts/check_staticduo_compatibility.py --repo . --upstream-ref upstream/main --candidate-ref FINAL_SHA --wheel EXTENSION_WHEEL
```

The first command reads the worktree. Its HEAD field is informational; an
uncommitted worktree is not a publishable release. The second checks committed
files. OAuth provenance is the actual historical raw file, with its declared
baseline an ancestor of the fetched upstream. A changed provider source requires
reconciliation of the core OAuth engine, adapter and tests before updating the
baseline/hash. Updating the range for a new minor core release requires reviewing
and testing the interface contracts. Neither a newer arbitrary SHA nor a matching
version alone proves compatibility.

The reviewed core range covers 1.106.x and 1.107.x and rejects 1.108.0.
The 1.107.0 review preserves the nine declared interface signatures and the
historical OAuth baseline and hash. Source contract tests cover both supported
minor versions, signature drift, historical provenance and release artifacts.
Runtime acceptance still belongs to the final built candidate.

## Build and Installed Runtime

Generate the catalog with `scripts/generate_staticduo_catalog.py`. After building
core and companion wheels plus the native binary from the final candidate:

```sh
python scripts/staticduo_release.py --repo . --upstream-ref upstream/main --candidate-ref FINAL_SHA --extension-wheel EXTENSION_WHEEL --native NATIVE_BINARY --catalog-dir GENERATED_CATALOG --output release-manifest.json
python scripts/check_staticduo_compatibility.py --repo . --upstream-ref upstream/main --candidate-ref FINAL_SHA --runtime --build-manifest release-manifest.json
```

The runtime probe starts isolated Python, checks actual installed wheel metadata,
refuses editable installs, validates active base/proxy dependencies, imports the
adapters and verifies native callable exports and binary hash. No invented native
`__version__` is required: the current Rust module does not export one. The receipt
binds the native source tree and binary hash, core source SHA, extension wheel/hash,
reviewed compatibility manifest, provider provenance and catalog source/overlay/
generated hashes. The generator output is rebuilt from candidate source/overlay
and exact bytes/provenance compared; self-declared artifact hashes alone do not
pass. Native receipt fields alone do not prove compiler provenance: retain actual
build logs/source identity with the registry digest. Build receipt labels must be applied by the image build pipeline;
this tool records expected values and does not build or publish images.

Registry publication is separate. Only after independent manifest/digest
verification should the publisher record `published_image_digest`, using
`docker.staticduo.com/litellm@sha256:...`. The private companion wheel is not a PyPI
release. Complete UI/native/image builds and real production Fedora acceptance
remain deployment responsibilities.

## Operational Artifacts and Promotion

The broker source is maintained at `docker/anthropic-subscription/native-sdk`
(package version 1.0.0). Record its installed files and hashes only when configured.
The quota controller is an independent operational release: inspect the actual
Fedora release mount from its deployment baseline, and record maintained source,
version/hash and configured profiles without credentials. Historical
`deploy/quota-sidecar/*.patch` files are not a new controller release source.
This extension refactor does not rewrite or deploy those components.

Initial modular B acceptance: candidate image publication, production Fedora
acceptance, main publication, then the same digest on NAS. Subsequent nightly
maintenance resumes its existing main-publication-before-Fedora sequence, while
always requiring Fedora acceptance before NAS. The nightly prompt records both
rules and the required upstream novelty/own insertion counts.

## Docker Source Receipt and Independent Guard

Before archiving the final committed build context, generate its frozen inputs:

```sh
python scripts/staticduo_release.py --prepare-source --repo WORKTREE --upstream-ref upstream/main --candidate-ref FINAL_SHA --output RELEASE_CONTEXT/staticduo-source.json
```

The root-level JSON is a generated release context input, not a tracked source
file. Docker requires it (default `STATICDUO_SOURCE_RECEIPT=staticduo-source.json`),
then runs the installed package in isolated Python after its final install. The
baker compares complete source inventory, metadata and catalog expected output,
checks native exports and dependencies, and records the actual native binary hash
at `/app/staticduo-release-manifest.json`. No Git checkout is required inside Docker.

The publisher supplies immutable image labels from that input:
`com.staticduo.extension.version`, `com.staticduo.extension.source.sha256`, and
`com.staticduo.compatibility.sha256`, plus the existing OCI revision. The independent
nightly guard checks these against actual installed source hashes and the baked
receipt, including native hash and revision. Any partial modular label set rejects.
Legacy images without modular markers keep their previous guard behavior.
