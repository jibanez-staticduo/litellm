"""Release gates reject incompatible source, wheels and installed native ABI."""

import json
import sys
import zipfile
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "extensions/staticduo-litellm/src"))
sys.path.insert(0, str(ROOT / "scripts"))
from check_staticduo_compatibility import check_candidate, check_wheel
from staticduo_litellm.compatibility.provider_upstream import ProviderUpstreamDriftError, check_provider_upstream_source
from staticduo_litellm.compatibility.release_manifest import (
    CompatibilityError,
    check_interfaces,
    check_runtime,
    check_versions,
    load_manifest,
)


def test_reviewed_source_contract():
    check_interfaces(load_manifest(), lambda path: (ROOT / path).read_bytes())


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


@pytest.mark.parametrize("core,extension", [("1.107.0", "0.1.0"), ("1.105.9", "0.1.0"), ("1.106.0", "0.2.0")])
def test_version_mismatch_rejected(core, extension):
    with pytest.raises(CompatibilityError):
        check_versions(load_manifest(), {"litellm": core, "staticduo-litellm": extension})


def test_patch_release_allowed():
    check_versions(load_manifest(), {"litellm": "1.106.99", "staticduo-litellm": "0.1.0"})


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
    manifest = load_manifest()
    wheel = tmp_path / "extension.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("staticduo_litellm-0.1.0.dist-info/METADATA", f"Name: staticduo-litellm\nVersion: {version}\n")
        for path in manifest.required_files:
            name = path.removeprefix("extensions/staticduo-litellm/src/")
            if name != omit:
                archive.writestr(name, (ROOT / path).read_bytes())
        archive.writestr("staticduo_litellm/compatibility/release-manifest.json", manifest.model_dump_json())
    return wheel


def test_wheel_requires_packaged_data(tmp_path):
    wheel = make_wheel(tmp_path, omit="staticduo_litellm/pricing/catalog-v1.json")
    with pytest.raises(CompatibilityError, match="modules/data"):
        check_wheel(wheel, load_manifest())


def test_wheel_version_rejected(tmp_path):
    with pytest.raises(CompatibilityError, match="version mismatch"):
        check_wheel(make_wheel(tmp_path, version="0.2.0"), load_manifest())


def test_complete_wheel_checked(tmp_path):
    result = check_wheel(make_wheel(tmp_path), load_manifest())
    assert len(result.sha256) == 64


def test_current_source_and_historical_provider_provenance():
    result = check_candidate(ROOT, load_manifest().upstream_baseline_commit)
    assert result.extension_version == "0.1.0"
    assert result.worktree is True


def test_declared_historical_provider_hash_rejected(monkeypatch):
    import check_staticduo_compatibility as gate

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
    import staticduo_release as release

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
    import generate_staticduo_catalog as generator
    import staticduo_release as release

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
