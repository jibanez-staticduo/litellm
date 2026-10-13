"""Release compatibility checks without importing providers or mutating core."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
from collections.abc import Mapping, Sequence
from importlib import metadata, resources
from pathlib import Path
from types import ModuleType
from typing import Final, Protocol

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from pydantic import BaseModel, ConfigDict


class CompatibilityError(RuntimeError):
    """The candidate does not satisfy the reviewed extension contract."""


class FrozenContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SignatureContract(FrozenContract):
    positional: tuple[str, ...]
    keyword_only: tuple[str, ...]
    defaults: int
    keyword_defaults: tuple[bool, ...]
    vararg: str | None
    kwarg: str | None
    is_async: bool


class InterfaceContract(FrozenContract):
    path: str
    symbol: str
    signature: SignatureContract


class ProviderContract(FrozenContract):
    path: str
    sha256: str


class NativeContract(FrozenContract):
    module: str
    callable_exports: tuple[str, ...]


class OperationalArtifact(FrozenContract):
    name: str
    source_path: str
    version: str | None = None
    scope: str


class ReleaseContract(FrozenContract):
    schema_version: int
    extension_version: str
    core_version_range: str
    upstream_baseline_commit: str
    provider_upstream: ProviderContract
    interfaces: tuple[InterfaceContract, ...]
    runtime_modules: tuple[str, ...]
    required_files: tuple[str, ...]
    native: NativeContract
    operational_artifacts: tuple[OperationalArtifact, ...]


class RuntimeEvidence(FrozenContract):
    core_version: str
    extension_version: str
    native_sha256: str


class CatalogSourceReceipt(FrozenContract):
    schema_version: int
    overlay_version: str
    overlay_sha256: str
    overlay_upstream_commit: str
    overlay_effective_baseline_commit: str
    source_sha256: str
    generated_sha256: str


class SourceReceipt(FrozenContract):
    schema_version: int = 1
    source_core_sha: str
    core_version: str
    extension_version: str
    compatibility_manifest_sha256: str
    extension_source_sha256: str
    extension_sources: Mapping[str, str]
    native_source_tree: str
    catalog: CatalogSourceReceipt


class BakedNativeReceipt(FrozenContract):
    sha256: str
    source_tree: str


class BakedReceipt(FrozenContract):
    schema_version: int = 1
    source_core_sha: str
    core_version: str
    extension_version: str
    compatibility_manifest_sha256: str
    extension_source_sha256: str
    native: BakedNativeReceipt
    catalog: CatalogSourceReceipt


def bake_receipt(source: SourceReceipt, catalog_dir: Path) -> BakedReceipt:
    manifest: Final = load_manifest()
    runtime: Final = check_runtime(manifest)
    installed: Final = metadata.files("staticduo-litellm")
    if installed is None:
        raise CompatibilityError("Installed extension source inventory unavailable")
    hashes: Final = {
        str(path): hashlib.sha256(Path(path.locate()).read_bytes()).hexdigest()
        for path in installed
        if str(path).startswith("staticduo_litellm/") and path.suffix in (".py", ".json")
    }
    inventory_hash: Final = hashlib.sha256(
        json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    manifest_hash: Final = hashlib.sha256(
        resources.files(__package__).joinpath("release-manifest.json").read_bytes()
    ).hexdigest()
    if (
        hashes != source.extension_sources
        or inventory_hash != source.extension_source_sha256
        or manifest_hash != source.compatibility_manifest_sha256
        or runtime.core_version != source.core_version
        or runtime.extension_version != source.extension_version
    ):
        raise CompatibilityError("Installed build differs from frozen source receipt")
    generated: Final = CatalogSourceReceipt.model_validate_json((catalog_dir / "manifest.json").read_bytes())
    if generated != source.catalog:
        raise CompatibilityError("Build catalog metadata differs from frozen source receipt")
    for name in ("model_prices_and_context_window.json", "model_prices_and_context_window_backup.json"):
        if hashlib.sha256((catalog_dir / name).read_bytes()).hexdigest() != source.catalog.generated_sha256:
            raise CompatibilityError("Build catalog bytes differ from frozen source receipt")
    return BakedReceipt(
        source_core_sha=source.source_core_sha,
        core_version=source.core_version,
        extension_version=source.extension_version,
        compatibility_manifest_sha256=manifest_hash,
        extension_source_sha256=inventory_hash,
        native=BakedNativeReceipt(sha256=runtime.native_sha256, source_tree=source.native_source_tree),
        catalog=generated,
    )


class BakeArguments(argparse.Namespace):
    source: Path
    catalog_dir: Path
    output: Path


def main() -> None:
    parser: Final = argparse.ArgumentParser(
        description="Bake verified installed runtime receipt from frozen source inputs"
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--catalog-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args: Final = BakeArguments()
    parser.parse_args(namespace=args)
    source: Final = SourceReceipt.model_validate_json(args.source.read_bytes())
    args.output.write_text(bake_receipt(source, args.catalog_dir).model_dump_json(indent=2) + "\n")


class SourceReader(Protocol):
    def __call__(self, path: str) -> bytes: ...


class VersionReader(Protocol):
    def __call__(self, distribution_name: str) -> str: ...


class RequirementsReader(Protocol):
    def __call__(self, distribution_name: str) -> Sequence[str] | None: ...


class ModuleImporter(Protocol):
    def __call__(self, name: str) -> ModuleType: ...


def load_manifest() -> ReleaseContract:
    return ReleaseContract.model_validate_json(
        resources.files(__package__).joinpath("release-manifest.json").read_text()
    )


def check_versions(manifest: ReleaseContract, versions: Mapping[str, str]) -> None:
    core: Final = versions.get("litellm", "")
    try:
        compatible: Final = core in SpecifierSet(manifest.core_version_range)
    except ValueError as error:
        raise CompatibilityError("Invalid core distribution version") from error
    if not compatible:
        raise CompatibilityError(f"Unsupported core version: {core}")
    if versions.get("staticduo-litellm") != manifest.extension_version:
        raise CompatibilityError("Extension distribution version does not match compatibility manifest")


def _find_function(tree: ast.Module, symbol: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    body: Sequence[ast.stmt] = tree.body  # rebind-ok: descend into each qualified symbol's AST body
    found: ast.stmt | None = None  # rebind-ok: traversal selects the current qualified symbol
    for name in symbol.split("."):
        matches = [
            item
            for item in body
            if isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
        ]
        if len(matches) != 1:
            raise CompatibilityError(f"Missing core interface: {symbol}")
        found = matches[0]
        body = found.body
    if not isinstance(found, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise CompatibilityError(f"Non-callable core interface: {symbol}")
    return found


def check_interfaces(manifest: ReleaseContract, read: SourceReader) -> None:
    for contract in manifest.interfaces:
        node = _find_function(ast.parse(read(contract.path)), contract.symbol)
        actual = SignatureContract(
            positional=tuple(arg.arg for arg in (*node.args.posonlyargs, *node.args.args)),
            keyword_only=tuple(arg.arg for arg in node.args.kwonlyargs),
            defaults=len(node.args.defaults),
            keyword_defaults=tuple(default is not None for default in node.args.kw_defaults),
            vararg=node.args.vararg.arg if node.args.vararg else None,
            kwarg=node.args.kwarg.arg if node.args.kwarg else None,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )
        if actual != contract.signature:
            raise CompatibilityError(f"Core interface signature changed: {contract.symbol}")
    for path in manifest.required_files:
        try:
            read(path)
        except (OSError, ValueError) as error:
            raise CompatibilityError(f"Missing extension module/data: {path}") from error


def check_runtime(
    manifest: ReleaseContract,
    *,
    version: VersionReader = metadata.version,
    importer: ModuleImporter = importlib.import_module,
    requirements: RequirementsReader = metadata.requires,
    expected_native_sha256: str | None = None,
) -> RuntimeEvidence:
    try:
        versions: Final = {name: version(name) for name in ("litellm", "staticduo-litellm")}
    except metadata.PackageNotFoundError as error:
        raise CompatibilityError("Core and extension must both be installed") from error
    check_versions(manifest, versions)
    for name in versions:
        for raw in requirements(name) or ():
            requirement = Requirement(raw)
            if requirement.marker and not any(requirement.marker.evaluate({"extra": extra}) for extra in ("", "proxy")):
                continue
            try:
                installed = version(requirement.name)
            except metadata.PackageNotFoundError as error:
                raise CompatibilityError(f"Missing runtime dependency: {requirement.name}") from error
            if installed not in requirement.specifier:
                raise CompatibilityError(f"Runtime dependency incompatible: {requirement.name}")
    try:
        native: Final = importer(manifest.native.module)
        for symbol in manifest.native.callable_exports:
            if not callable(getattr(native, symbol, None)):
                raise CompatibilityError(f"Native ABI export missing: {symbol}")
        if native.__file__ is None:
            raise CompatibilityError("Native module has no installed binary")
        native_hash: Final = hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest()
        if expected_native_sha256 is not None and native_hash != expected_native_sha256:
            raise CompatibilityError("Installed native binary differs from build manifest")
        for module in manifest.runtime_modules:
            importer(module)
    except ImportError as error:
        raise CompatibilityError("Required runtime module is unavailable") from error
    return RuntimeEvidence(
        core_version=versions["litellm"], extension_version=versions["staticduo-litellm"], native_sha256=native_hash
    )


if __name__ == "__main__":
    main()
