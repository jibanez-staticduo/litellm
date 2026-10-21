"""Release gates reject incompatible source, wheels and installed native ABI."""

import json
import sys
import tomllib
import zipfile
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
from staticduo_litellm.compatibility.provider_upstream import ProviderUpstreamDriftError, check_provider_upstream_source
from staticduo_litellm.compatibility.release_manifest import (
    CompatibilityError,
    check_interfaces,
    check_runtime,
    check_versions,
    load_manifest,
)

from scripts.check_staticduo_compatibility import check_candidate, check_wheel, extension_inventory


def test_reviewed_source_contract():
    candidate = check_candidate(ROOT, load_manifest().upstream_baseline_commit)
    assert candidate.core_version == tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert len(candidate.extension_source_sha256) == 64


def test_signature_drift_rejected():
    manifest = load_manifest()

    def read(path):
        raw = (ROOT / path).read_bytes()
        return raw.replace(b"def get_access_token(self)", b"def get_access_token(self, changed)")

    with pytest.raises(CompatibilityError, match="signature changed"):
        check_interfaces(manifest, read)


def test_missing_extension_module_rejected():
    manifest = load_manifest()

    def read(path):
        if path == manifest.required_files[0]:
            raise FileNotFoundError(path)
        return (ROOT / path).read_bytes()

    with pytest.raises(CompatibilityError, match="Missing extension"):
        check_interfaces(manifest, read)


@pytest.mark.parametrize("core,extension", [("1.109.0", "0.1.0"), ("1.105.9", "0.1.0"), ("1.106.0", "0.2.0")])
def test_version_mismatch_rejected(core, extension):
    with pytest.raises(CompatibilityError):
        check_versions(load_manifest(), {"litellm": core, "staticduo-litellm": extension})


@pytest.mark.parametrize("core", ["1.106.0", "1.106.99", "1.107.0", "1.107.99", "1.108.0", "1.108.99"])
def test_reviewed_minor_and_patch_releases_allowed(core):
    assert check_versions(load_manifest(), {"litellm": core, "staticduo-litellm": "0.1.0"}) is None


def test_upstream_drift_rejected():
    with pytest.raises(ProviderUpstreamDriftError):
        check_provider_upstream_source(b"changed upstream OAuth algorithm")


def runtime_fixture(tmp_path):
    native = tmp_path / "_native.abi3.so"
    native.write_bytes(b"fixture binary")
    module = SimpleNamespace(__file__=str(native))
    for name in load_manifest().native.callable_exports:
        setattr(module, name, lambda: None)
    return module


def test_native_export_drift_rejected(tmp_path):
    native = runtime_fixture(tmp_path)
    del native.aresponses
    with pytest.raises(CompatibilityError, match="Native ABI export missing"):
        check_runtime(
            load_manifest(),
            version=lambda name: {"litellm": "1.106.0", "staticduo-litellm": "0.1.0"}[name],
            requirements=lambda name: [],
            importer=lambda name: native,
        )


def test_native_hash_mismatch_rejected(tmp_path):
    with pytest.raises(CompatibilityError, match="binary differs"):
        check_runtime(
            load_manifest(),
            version=lambda name: {"litellm": "1.106.0", "staticduo-litellm": "0.1.0"}[name],
            requirements=lambda name: [],
            importer=lambda name: runtime_fixture(tmp_path),
            expected_native_sha256="0" * 64,
        )


def test_missing_installed_extension_rejected():
    def version(name):
        raise metadata.PackageNotFoundError(name)

    with pytest.raises(CompatibilityError, match="both be installed"):
        check_runtime(load_manifest(), version=version)


def test_dependency_mismatch_rejected(tmp_path):
    versions = {"litellm": "1.106.0", "staticduo-litellm": "0.1.0", "httpx": "0.20.0"}
    with pytest.raises(CompatibilityError, match="dependency incompatible"):
        check_runtime(
            load_manifest(),
            version=versions.__getitem__,
            requirements=lambda name: ["httpx>=0.28.0"],
            importer=lambda name: runtime_fixture(tmp_path),
        )


def make_wheel(tmp_path, *, omit=None, version="0.1.0"):
    wheel = tmp_path / "extension.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("staticduo_litellm-0.1.0.dist-info/METADATA", f"Name: staticduo-litellm\nVersion: {version}\n")
        for name in extension_inventory(ROOT):
            path = "extensions/staticduo-litellm/src/" + name
            if name != omit:
                archive.writestr(name, (ROOT / path).read_bytes())
    return wheel


def test_wheel_requires_packaged_data(tmp_path):
    wheel = make_wheel(tmp_path, omit="staticduo_litellm/pricing/catalog-v1.json")
    with pytest.raises(CompatibilityError, match="modules/data"):
        check_wheel(wheel, load_manifest(), extension_inventory(ROOT))


def test_wheel_version_rejected(tmp_path):
    with pytest.raises(CompatibilityError, match="version mismatch"):
        check_wheel(make_wheel(tmp_path, version="0.2.0"), load_manifest(), extension_inventory(ROOT))


def test_complete_wheel_checked(tmp_path):
    result = check_wheel(make_wheel(tmp_path), load_manifest(), extension_inventory(ROOT))
    assert len(result.sha256) == 64


def test_current_source_and_historical_provider_provenance():
    result = check_candidate(ROOT, load_manifest().upstream_baseline_commit)
    assert result.extension_version == "0.1.0"
    assert result.worktree is True


def test_declared_historical_provider_hash_rejected(monkeypatch):
    from scripts import check_staticduo_compatibility as gate

    original = gate.git

    def changed_history(repo, *args):
        if args == ("show", f"{load_manifest().upstream_baseline_commit}:{load_manifest().provider_upstream.path}"):
            return b"arbitrary historical bytes"
        return original(repo, *args)

    monkeypatch.setattr(gate, "git", changed_history)
    with pytest.raises(CompatibilityError, match="historical provenance"):
        gate.check_candidate(ROOT, load_manifest().upstream_baseline_commit)


def test_required_runtime_module_missing(tmp_path):
    native = runtime_fixture(tmp_path)

    def importer(name):
        if name == load_manifest().native.module:
            return native
        raise ImportError(name)

    with pytest.raises(CompatibilityError, match="Required runtime module"):
        check_runtime(
            load_manifest(),
            version=lambda name: {"litellm": "1.106.0", "staticduo-litellm": "0.1.0"}[name],
            requirements=lambda name: [],
            importer=importer,
        )


@pytest.mark.parametrize(
    "symbol",
    [
        "CustomLogger.async_post_call_streaming_iterator_hook",
        "_get_allowed_mcp_servers",
        "call_mcp_tool",
        "catalog_operation",
        "MCPServerManager.resolve_toolset_tool_permissions",
    ],
)
def test_critical_interface_missing_rejected(symbol):
    manifest = load_manifest()
    target = next(item for item in manifest.interfaces if item.symbol == symbol)

    def read(path):
        source = (ROOT / path).read_bytes()
        return (
            source.replace(target.symbol.split(".")[-1].encode(), b"contract_removed")
            if path == target.path
            else source
        )

    with pytest.raises(CompatibilityError, match="Missing core interface"):
        check_interfaces(manifest, read)


def test_release_rejects_catalog_source_tampering(tmp_path, monkeypatch):
    from scripts import staticduo_release as release

    manifest = load_manifest()
    monkeypatch.setattr(
        release, "check_candidate", lambda *args: SimpleNamespace(manifest=manifest, candidate_revision="a" * 40)
    )
    monkeypatch.setattr(release, "git", lambda *args: b"reviewed source")
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "overlay_version": "v1",
                "overlay_sha256": "0" * 64,
                "overlay_upstream_commit": "a" * 40,
                "overlay_effective_baseline_commit": "b" * 40,
                "source_sha256": "0" * 64,
                "generated_sha256": "0" * 64,
            }
        )
    )
    with pytest.raises(CompatibilityError, match="Catalog source"):
        release.create_release(ROOT, "upstream/main", "candidate", tmp_path / "wheel", tmp_path / "native", catalog)


def test_complete_release_binds_catalog_wheel_and_native(tmp_path, monkeypatch):
    from scripts import generate_staticduo_catalog as generator
    from scripts import staticduo_release as release

    candidate = check_candidate(ROOT, load_manifest().upstream_baseline_commit)
    monkeypatch.setattr(release, "check_candidate", lambda *args: candidate)

    def source_git(repo, *arguments):
        if arguments[0] == "rev-parse":
            return b"a" * 40
        path = arguments[1].split(":", 1)[1]
        return (ROOT / path).read_bytes()

    monkeypatch.setattr(release, "git", source_git)
    catalog = tmp_path / "catalog"
    generator.generate_catalog(ROOT / "model_prices_and_context_window.json", catalog)
    binary = tmp_path / "_native.abi3.so"
    binary.write_bytes(b"built native fixture")
    receipt = release.create_release(ROOT, "upstream/main", "candidate", make_wheel(tmp_path), binary, catalog)
    assert receipt.source_core_sha == candidate.candidate_revision
    assert receipt.extension_version == "0.1.0"
    assert receipt.catalog.source_sha256 != receipt.catalog.generated_sha256
    assert receipt.native.source_tree == "a" * 40
    assert receipt.image_labels["com.staticduo.native.sha256"] == receipt.native.sha256
    assert receipt.published_image_digest is None
    (catalog / "model_prices_and_context_window.json").write_bytes(b"tampered generated file")
    with pytest.raises(CompatibilityError, match="Generated catalog differs"):
        release.create_release(ROOT, "upstream/main", "candidate", make_wheel(tmp_path), binary, catalog)


@pytest.mark.parametrize(
    "module",
    [
        "staticduo_litellm/codex/portable.py",
        "staticduo_litellm/lazy/engine.py",
        "staticduo_litellm/providers/chatgpt/authenticator.py",
    ],
)
def test_wheel_requires_every_candidate_module(tmp_path, module):
    with pytest.raises(CompatibilityError, match="modules/data"):
        check_wheel(make_wheel(tmp_path, omit=module), load_manifest(), extension_inventory(ROOT))


def test_wheel_matching_version_and_manifest_rejects_stale_code(tmp_path):
    wheel = make_wheel(tmp_path)
    stale = tmp_path / "stale.whl"
    with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(stale, "w") as target:
        for name in source.namelist():
            raw = source.read(name)
            target.writestr(
                name,
                raw + b"\n# previous release implementation\n"
                if name == "staticduo_litellm/codex/portable.py"
                else raw,
            )
    with pytest.raises(CompatibilityError, match="source differs from reviewed candidate"):
        check_wheel(stale, load_manifest(), extension_inventory(ROOT))


def test_wheel_frozen_candidate_inventory_rejects_worktree_delta(tmp_path):
    inventory = extension_inventory(ROOT)
    wheel = make_wheel(tmp_path)
    changed_inventory = {**inventory, "staticduo_litellm/codex/portable.py": "0" * 64}
    with pytest.raises(CompatibilityError, match="source differs from reviewed candidate"):
        check_wheel(wheel, load_manifest(), changed_inventory)


def test_catalog_self_declared_hash_cannot_hide_wrong_generated_output(tmp_path, monkeypatch):
    import hashlib

    from scripts import generate_staticduo_catalog as generator
    from scripts import staticduo_release as release

    candidate = check_candidate(ROOT, load_manifest().upstream_baseline_commit)
    monkeypatch.setattr(release, "check_candidate", lambda *args: candidate)

    def source_git(repo, *arguments):
        if arguments[0] == "rev-parse":
            return b"a" * 40
        return (ROOT / arguments[1].split(":", 1)[1]).read_bytes()

    monkeypatch.setattr(release, "git", source_git)
    catalog = tmp_path / "catalog"
    generator.generate_catalog(ROOT / "model_prices_and_context_window.json", catalog)
    malicious = b'{"incorrect_catalog":{}}\n'
    for filename in ("model_prices_and_context_window.json", "model_prices_and_context_window_backup.json"):
        (catalog / filename).write_bytes(malicious)
    receipt = json.loads((catalog / "manifest.json").read_text())
    receipt["generated_sha256"] = hashlib.sha256(malicious).hexdigest()
    (catalog / "manifest.json").write_text(json.dumps(receipt))
    with pytest.raises(CompatibilityError, match="reproducible candidate output"):
        release.create_release(ROOT, "upstream/main", "candidate", make_wheel(tmp_path), tmp_path / "native", catalog)


def test_baker_rejects_installed_source_and_catalog_drift(tmp_path, monkeypatch):
    from staticduo_litellm.compatibility import release_manifest as contracts

    from scripts import generate_staticduo_catalog as generator
    from scripts import staticduo_release as release
    from scripts.check_staticduo_compatibility import inventory_sha256

    source = release.prepare_source(ROOT, load_manifest().upstream_baseline_commit, "HEAD")
    inventory = extension_inventory(ROOT)
    source = source.model_copy(
        update={
            "extension_sources": inventory,
            "extension_source_sha256": inventory_sha256(inventory),
            "compatibility_manifest_sha256": inventory["staticduo_litellm/compatibility/release-manifest.json"],
        }
    )
    paths = []
    for name in inventory:
        path = metadata.PackagePath(name)
        path.dist = SimpleNamespace(locate_file=lambda item: ROOT / "extensions/staticduo-litellm/src" / str(item))
        paths.append(path)
    monkeypatch.setattr(contracts.metadata, "files", lambda name: paths)
    monkeypatch.setattr(
        contracts,
        "check_runtime",
        lambda manifest: contracts.RuntimeEvidence(
            core_version=source.core_version, extension_version="0.1.0", native_sha256="a" * 64
        ),
    )
    catalog = tmp_path / "catalog"
    generator.generate_catalog(ROOT / "model_prices_and_context_window.json", catalog)
    source = source.model_copy(
        update={"catalog": contracts.CatalogSourceReceipt.model_validate_json((catalog / "manifest.json").read_bytes())}
    )
    receipt = contracts.bake_receipt(source, catalog)
    assert receipt.source_core_sha == source.source_core_sha
    assert receipt.native.sha256 == "a" * 64
    bad_source = source.model_copy(update={"extension_source_sha256": "0" * 64})
    with pytest.raises(CompatibilityError, match="frozen source receipt"):
        contracts.bake_receipt(bad_source, catalog)
    bad_manifest = source.model_copy(update={"compatibility_manifest_sha256": "0" * 64})
    with pytest.raises(CompatibilityError, match="frozen source receipt"):
        contracts.bake_receipt(bad_manifest, catalog)
    (catalog / "model_prices_and_context_window.json").write_bytes(b"wrong catalog")
    with pytest.raises(CompatibilityError, match="Build catalog bytes"):
        contracts.bake_receipt(source, catalog)


def test_prepare_source_cli_rejects_mixed_artifacts_and_release_requires_artifacts(monkeypatch, tmp_path):
    from scripts import staticduo_release as release

    base = [
        "release",
        "--repo",
        str(ROOT),
        "--upstream-ref",
        "upstream/main",
        "--candidate-ref",
        "HEAD",
        "--output",
        str(tmp_path / "receipt.json"),
    ]
    monkeypatch.setattr(sys, "argv", [*base, "--prepare-source", "--native", "arbitrary.so"])
    with pytest.raises(SystemExit) as rejected:
        release.main()
    assert rejected.value.code == 2
    monkeypatch.setattr(sys, "argv", base)
    with pytest.raises(SystemExit) as rejected:
        release.main()
    assert rejected.value.code == 2
    assert not (tmp_path / "receipt.json").exists()
