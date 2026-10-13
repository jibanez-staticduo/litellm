"""Create a receipt binding source, extension, catalog and native builds.

Registry publication and digest verification are separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final

if __package__:
    from .check_staticduo_compatibility import CompatibilityError, WheelReceipt, check_candidate, check_wheel, git
else:
    from check_staticduo_compatibility import CompatibilityError, WheelReceipt, check_candidate, check_wheel, git
from pydantic import BaseModel, ConfigDict, JsonValue, RootModel
from staticduo_litellm.compatibility.release_manifest import (
    CatalogSourceReceipt,
    FrozenContract,
    OperationalArtifact,
    ProviderContract,
    SourceReceipt,
)
from staticduo_litellm.pricing import catalog as catalog_policy


class CatalogReceipt(FrozenContract):
    schema_version: int
    overlay_version: str
    overlay_sha256: str
    overlay_upstream_commit: str
    overlay_effective_baseline_commit: str
    source_sha256: str
    generated_sha256: str


class NativeReceipt(FrozenContract):
    module: str
    callable_exports: tuple[str, ...]
    file: str
    sha256: str
    source_tree: str


class OverlayIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: int
    overlay_version: str
    upstream_commit: str
    effective_baseline_commit: str


class ReleaseReceipt(FrozenContract):
    schema_version: int = 1
    source_core_sha: str
    core_version: str
    extension_version: str
    compatibility_manifest_sha256: str
    extension_source_sha256: str
    provider_upstream: ProviderContract
    provider_baseline_commit: str
    upstream_revision: str
    extension_wheel: WheelReceipt
    catalog: CatalogReceipt
    native: NativeReceipt
    image_labels: Mapping[str, str]
    operational_artifacts: tuple[OperationalArtifact, ...]
    published_image_digest: str | None = None


class ReleaseArguments(argparse.Namespace):
    repo: Path
    upstream_ref: str
    candidate_ref: str
    extension_wheel: Path | None
    native: Path | None
    catalog_dir: Path | None
    output: Path
    published_digest: str | None
    prepare_source: bool


def prepare_source(repo: Path, upstream_ref: str, candidate_ref: str) -> SourceReceipt:
    result: Final = check_candidate(repo, upstream_ref, candidate_ref)
    revision: Final = result.candidate_revision
    source: Final = git(repo, "show", f"{revision}:model_prices_and_context_window.json")
    overlay: Final = RootModel[Mapping[str, JsonValue]].model_validate_json(
        git(repo, "show", f"{revision}:extensions/staticduo-litellm/src/staticduo_litellm/pricing/catalog-v1.json")
    )
    policy: Final = git(
        repo, "show", f"{revision}:extensions/staticduo-litellm/src/staticduo_litellm/pricing/catalog.py"
    )
    if policy != Path(catalog_policy.__file__).read_bytes():
        raise CompatibilityError("Release tool catalog policy differs from reviewed candidate")
    identity: Final = OverlayIdentity.model_validate(overlay.root)
    catalog: Final = RootModel[Mapping[str, JsonValue]].model_validate_json(source)
    generated: Final = (
        json.dumps(catalog_policy.apply_catalog_overlay(catalog.root, overlay.root), indent=4) + "\n"
    ).encode()
    return SourceReceipt(
        source_core_sha=revision,
        core_version=result.core_version,
        extension_version=result.extension_version,
        compatibility_manifest_sha256=result.compatibility_manifest_sha256,
        extension_source_sha256=result.extension_source_sha256,
        extension_sources=result.extension_sources,
        native_source_tree=git(repo, "rev-parse", f"{revision}:litellm-rust").decode().strip(),
        catalog=CatalogSourceReceipt(
            schema_version=identity.schema_version,
            overlay_version=identity.overlay_version,
            overlay_sha256=hashlib.sha256(
                json.dumps(overlay.root, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            overlay_upstream_commit=identity.upstream_commit,
            overlay_effective_baseline_commit=identity.effective_baseline_commit,
            source_sha256=hashlib.sha256(source).hexdigest(),
            generated_sha256=hashlib.sha256(generated).hexdigest(),
        ),
    )


def create_release(
    repo: Path,
    upstream_ref: str,
    candidate_ref: str,
    wheel: Path,
    native: Path,
    catalog: Path,
    published_digest: str | None = None,
) -> ReleaseReceipt:
    result: Final = check_candidate(repo, upstream_ref, candidate_ref)
    manifest: Final = result.manifest
    generated: Final = CatalogReceipt.model_validate_json((catalog / "manifest.json").read_bytes())
    revision: Final = result.candidate_revision
    source: Final = git(repo, "show", f"{revision}:model_prices_and_context_window.json")
    if hashlib.sha256(source).hexdigest() != generated.source_sha256:
        raise CompatibilityError("Catalog source is not the reviewed candidate source")
    overlay: Final = RootModel[Mapping[str, JsonValue]].model_validate_json(
        git(repo, "show", f"{revision}:extensions/staticduo-litellm/src/staticduo_litellm/pricing/catalog-v1.json")
    )
    overlay_bytes: Final = json.dumps(overlay.root, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(overlay_bytes).hexdigest() != generated.overlay_sha256:
        raise CompatibilityError("Catalog overlay differs from reviewed candidate overlay")
    identity: Final = OverlayIdentity.model_validate(overlay.root)
    if (
        generated.schema_version != identity.schema_version
        or generated.overlay_version != identity.overlay_version
        or generated.overlay_upstream_commit != identity.upstream_commit
        or generated.overlay_effective_baseline_commit != identity.effective_baseline_commit
    ):
        raise CompatibilityError("Catalog provenance metadata differs from reviewed overlay")
    policy_source: Final = git(
        repo, "show", f"{revision}:extensions/staticduo-litellm/src/staticduo_litellm/pricing/catalog.py"
    )
    if policy_source != Path(catalog_policy.__file__).read_bytes():
        raise CompatibilityError("Release tool catalog policy differs from reviewed candidate")
    source_catalog: Final = RootModel[Mapping[str, JsonValue]].model_validate_json(source)
    expected_catalog: Final = (
        json.dumps(catalog_policy.apply_catalog_overlay(source_catalog.root, overlay.root), indent=4) + "\n"
    ).encode()
    if hashlib.sha256(expected_catalog).hexdigest() != generated.generated_sha256:
        raise CompatibilityError("Generated catalog hash differs from reproducible candidate output")
    for filename in ("model_prices_and_context_window.json", "model_prices_and_context_window_backup.json"):
        if (catalog / filename).read_bytes() != expected_catalog:
            raise CompatibilityError("Generated catalog differs from catalog build manifest")
    if published_digest and not re.fullmatch(r"docker\.staticduo\.com/litellm@sha256:[0-9a-f]{64}", published_digest):
        raise CompatibilityError("Published image must be the registry digest reference")
    native_hash: Final = hashlib.sha256(native.read_bytes()).hexdigest()
    return ReleaseReceipt(
        source_core_sha=revision,
        core_version=result.core_version,
        extension_version=result.extension_version,
        compatibility_manifest_sha256=result.compatibility_manifest_sha256,
        extension_source_sha256=result.extension_source_sha256,
        provider_upstream=manifest.provider_upstream,
        provider_baseline_commit=manifest.upstream_baseline_commit,
        upstream_revision=result.upstream_revision,
        extension_wheel=check_wheel(wheel, manifest, result.extension_sources),
        catalog=generated,
        native=NativeReceipt(
            module=manifest.native.module,
            callable_exports=manifest.native.callable_exports,
            file=native.name,
            sha256=native_hash,
            source_tree=git(repo, "rev-parse", f"{revision}:litellm-rust").decode().strip(),
        ),
        image_labels={
            "org.opencontainers.image.revision": revision,
            "com.staticduo.extension.version": result.extension_version,
            "com.staticduo.compatibility.sha256": result.compatibility_manifest_sha256,
            "com.staticduo.native.sha256": native_hash,
        },
        operational_artifacts=manifest.operational_artifacts,
        published_image_digest=published_digest,
    )


def main() -> None:
    parser: Final = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--upstream-ref", required=True)
    parser.add_argument("--candidate-ref", required=True)
    parser.add_argument(
        "--prepare-source", action="store_true", help="Write frozen inputs for the Docker build context"
    )
    parser.add_argument("--extension-wheel", type=Path)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--catalog-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--published-digest", help="Record only after independent registry manifest verification")
    args: Final = ReleaseArguments()
    parser.parse_args(namespace=args)
    if args.prepare_source:
        if args.extension_wheel or args.native or args.catalog_dir or args.published_digest:
            parser.error("Source preparation does not accept built artifacts or published digest")
        args.output.write_text(
            prepare_source(args.repo, args.upstream_ref, args.candidate_ref).model_dump_json(indent=2) + "\n"
        )
        return
    if args.extension_wheel is None or args.native is None or args.catalog_dir is None:
        parser.error("Release receipt requires --extension-wheel, --native and --catalog-dir")
    result: Final = create_release(
        args.repo,
        args.upstream_ref,
        args.candidate_ref,
        args.extension_wheel,
        args.native,
        args.catalog_dir,
        args.published_digest,
    )
    args.output.write_text(result.model_dump_json(indent=2) + "\n")


if __name__ == "__main__":
    main()
