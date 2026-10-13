# Compatibility and Release Contract

`compatibility/release-manifest.json` is packaged with the extension. It defines
extension version, supported core versions, reviewed upstream OAuth provenance,
critical callback/MCP/OAuth signatures, required data/modules and Rust exports.
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
generated hashes. Build receipt labels must be applied by the image build pipeline;
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
