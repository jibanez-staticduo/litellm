import email
import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Final
from unittest.mock import patch

import pytest
from packaging.requirements import Requirement

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


ROOT: Final = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("sdist_only", [False, True])
def test_build_command_selects_requested_distributions(tmp_path: Path, sdist_only: bool) -> None:
    from scripts.build_core_distribution import main

    output: Final = tmp_path / "dist"
    arguments: Final = ["build_core_distribution.py", "--out-dir", str(output)] + (
        ["--sdist-only"] if sdist_only else []
    )
    with (
        patch.object(sys, "argv", arguments),
        patch("scripts.build_core_distribution.stage_core_distribution") as stage,
        patch("scripts.build_core_distribution.subprocess.run") as run,
    ):
        main()
        assert run.call_count == 2
        companion_command: Final = run.call_args_list[0].args[0]
        assert companion_command[companion_command.index("--package") + 1] == "staticduo-litellm"
        assert ("--sdist" in companion_command) is sdist_only
        assert ("--wheel" in companion_command) is not sdist_only
        command: Final = run.call_args_list[1].args[0]
        assert command[:2] == ["uv", "build"]
        assert ("--sdist" in command) is sdist_only
        assert "--wheel" not in command
        assert command[command.index("--out-dir") + 1] == str(output)
        assert run.call_args.kwargs["check"] is True
        assert run.call_args.kwargs["cwd"] == stage.call_args.args[1]
    assert not stage.call_args.args[1].exists()


@pytest.fixture
def source_repository(tmp_path: Path) -> Path:
    source: Final = tmp_path / "source"
    source.mkdir()
    subprocess.run(["git", "init", "--quiet", str(source)], check=True)
    return source


def test_staging_stamps_release_version_without_modifying_sources(tmp_path: Path, source_repository: Path) -> None:
    from scripts.build_core_distribution import SOURCES, stage_core_distribution

    source: Final = source_repository
    for name in SOURCES:
        path: Final = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if name == "extensions/staticduo-litellm":
            path.mkdir()
            (path / "pyproject.toml").write_text('[project]\nname = "staticduo-litellm"\nversion = "0.1.0"\n')
        else:
            path.write_text(f"shared {name}")
    (source / "pyproject.toml").write_text('[project]\nname = "litellm"\nversion = "9.8.7rc1"\n')
    manifest: Final = source / "packaging/litellm-core/pyproject.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes((ROOT / "packaging/litellm-core/pyproject.toml").read_bytes())
    original: Final = manifest.read_bytes()
    stage: Final = tmp_path / "stage"
    stage_core_distribution(source, stage)
    assert tomllib.loads((stage / "pyproject.toml").read_text())["project"]["version"] == "9.8.7rc1"
    assert manifest.read_bytes() == original
    assert (source / "pyproject.toml").read_text() == '[project]\nname = "litellm"\nversion = "9.8.7rc1"\n'
    assert all(
        (stage / name).read_bytes() == (source / name).read_bytes()
        for name in SOURCES
        if name != "extensions/staticduo-litellm"
    )
    assert (stage / "extensions/staticduo-litellm/pyproject.toml").read_bytes() == (
        source / "extensions/staticduo-litellm/pyproject.toml"
    ).read_bytes()


@pytest.fixture(scope="module")
def distribution_directory() -> Path:
    directory: Final = os.environ.get("CORE_DISTRIBUTION_DIR")
    if directory is None:
        pytest.skip("CORE_DISTRIBUTION_DIR is supplied by the installed-distribution CI job")
    return Path(directory)


@pytest.fixture(scope="module")
def distributions(distribution_directory: Path) -> tuple[Path, Path]:
    wheels: Final = tuple(distribution_directory.glob("litellm_core-*.whl"))
    sdists: Final = tuple(distribution_directory.glob("litellm_core-*.tar.gz"))
    assert len(wheels) == len(sdists) == 1
    return wheels[0], sdists[0]


def test_core_wheel_metadata_and_resources(distributions: tuple[Path, Path]) -> None:
    with zipfile.ZipFile(distributions[0]) as wheel:
        names: Final = wheel.namelist()
        metadata: Final = email.message_from_bytes(
            wheel.read(next(n for n in names if n.endswith(".dist-info/METADATA")))
        )
        assert metadata["Name"] == "litellm-core"
        assert metadata["Version"] == tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
        assert not metadata.get_all("Provides-Extra")
        assert not any(n.endswith(".dist-info/entry_points.txt") for n in names)
        requirements: Final = tomllib.loads((ROOT / "packaging/litellm-core/pyproject.toml").read_text())["project"][
            "dependencies"
        ]
        for python_version in ("3.10", "3.11", "3.12", "3.13", "3.14"):
            environment: Final = {"python_version": python_version, "python_full_version": python_version + ".0"}
            assert {
                (requirement.name, requirement.specifier, frozenset(requirement.extras))
                for item in metadata.get_all("Requires-Dist", ())
                for requirement in (Requirement(item),)
                if requirement.marker is None or requirement.marker.evaluate(environment)
            } == {
                (requirement.name, requirement.specifier, frozenset(requirement.extras))
                for item in requirements
                for requirement in (Requirement(item),)
                if requirement.marker is None or requirement.marker.evaluate(environment)
            }
        assert "litellm/model_prices_and_context_window_backup.json" in names
        assert "litellm/router_strategy/complexity_router/fuse_presets.json" in names
        assert "litellm/proxy/proxy_cli.py" in names
        assert any(n.startswith("litellm/rust_bridge/_native.") and n.endswith((".so", ".pyd")) for n in names)
        assert not any(n.startswith("litellm/proxy/_experimental/out/") for n in names)


def test_core_artifacts_exclude_local_configuration(distributions: tuple[Path, Path]) -> None:
    configurations: Final = (
        "litellm/proxy/_new_secret_config.yaml",
        "litellm/proxy/_new_new_secret_config.yaml",
        "litellm/proxy/_super_secret_config.yaml",
    )
    with zipfile.ZipFile(distributions[0]) as wheel, tarfile.open(distributions[1]) as archive:
        for name in configurations:
            assert name not in wheel.namelist(), f"Core wheel contains ignored configuration {name}"
            assert not any(member.name.endswith(f"/{name}") for member in archive.getmembers())


@pytest.mark.parametrize(
    "relative_path",
    [
        "rust-toolchain.toml",
        ".cargo/config.toml",
        "extensions/staticduo-litellm/pyproject.toml",
        "extensions/staticduo-litellm/src/staticduo_litellm/codex/portable.py",
        "extensions/staticduo-litellm/src/staticduo_litellm/pricing/catalog-v1.json",
    ],
)
def test_core_sdist_preserves_native_build_configuration(distribution_directory: Path, relative_path: str) -> None:
    sdists: Final = tuple(distribution_directory.glob("litellm_core-*.tar.gz"))
    assert len(sdists) == 1
    with tarfile.open(sdists[0]) as archive:
        name: Final = f"{sdists[0].name.removesuffix('.tar.gz')}/{relative_path}"
        assert name in archive.getnames(), f"Core source distribution is missing {relative_path}"
        content: Final = archive.extractfile(name)
        assert content is not None
        assert content.read() == (ROOT / relative_path).read_bytes()


def test_core_sdist_rebuilds_without_repository(distributions: tuple[Path, Path], tmp_path: Path) -> None:
    with tarfile.open(distributions[1]) as archive:
        archive.extractall(tmp_path, filter="data")
    source: Final = next(tmp_path.glob("litellm_core-*"))
    assert not (source / "scripts/build_core_distribution.py").exists()
    assert tomllib.loads((source / "pyproject.toml").read_text())["project"]["name"] == "litellm-core"
    result: Final = subprocess.run(
        [
            "uv",
            "build",
            "--all-packages",
            "--python",
            sys.executable,
            "--wheel",
            "--out-dir",
            str(tmp_path / "rebuilt"),
        ],
        cwd=source,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    rebuilt: Final = next((tmp_path / "rebuilt").glob("litellm_core-*.whl"))
    companion: Final = next((tmp_path / "rebuilt").glob("staticduo_litellm-*.whl"))
    with zipfile.ZipFile(companion) as extension:
        assert "staticduo_litellm/codex/portable.py" in extension.namelist()
        assert "staticduo_litellm/pricing/catalog-v1.json" in extension.namelist()
    with zipfile.ZipFile(distributions[0]) as original, zipfile.ZipFile(rebuilt) as wheel:
        assert set(original.namelist()) == set(wheel.namelist())
        for name in original.namelist():
            if (name.startswith("litellm/") or name.endswith("/METADATA")) and not name.endswith((".so", ".pyd")):
                assert original.read(name) == wheel.read(name), name


def test_staging_copies_sources_without_build_artifacts(tmp_path: Path, source_repository: Path) -> None:
    from scripts.build_core_distribution import SOURCES, stage_core_distribution

    source: Final = source_repository
    for name in SOURCES:
        (source / name).mkdir(parents=True, exist_ok=True)
        (source / name / "shared.txt").write_text("source payload")
        (source / name / "stale.so").write_text("old native extension")
        (source / name / "__pycache__").mkdir()
        (source / name / "__pycache__/old.pyc").write_bytes(b"stale bytecode")
    (source / "extensions/staticduo-litellm/pyproject.toml").write_text(
        '[project]\nname = "staticduo-litellm"\nversion = "0.1.0"\n'
    )
    (source / "pyproject.toml").write_text('[project]\nname = "litellm"\nversion = "1.2.3"\n')
    manifest: Final = source / "packaging/litellm-core/pyproject.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes((ROOT / "packaging/litellm-core/pyproject.toml").read_bytes())
    stage: Final = tmp_path / "stage"
    stage_core_distribution(source, stage)
    assert all((stage / name / "shared.txt").read_text() == "source payload" for name in SOURCES)
    assert not tuple(stage.rglob("*.so"))
    assert not tuple(stage.rglob("*.pyc"))
    assert all((source / name / "stale.so").is_file() for name in SOURCES)


def test_staging_preserves_gitignore_rules(tmp_path: Path, source_repository: Path) -> None:
    from scripts.build_core_distribution import SOURCES, stage_core_distribution

    source: Final = source_repository
    for name in SOURCES:
        (source / name).mkdir(parents=True, exist_ok=True)
        (source / name / "shared.txt").write_text("shared payload")
    (source / "extensions/staticduo-litellm/pyproject.toml").write_text(
        '[project]\nname = "staticduo-litellm"\nversion = "0.1.0"\n'
    )
    (source / "pyproject.toml").write_text('[project]\nname = "litellm"\nversion = "1.2.3"\n')
    manifest: Final = source / "packaging/litellm-core/pyproject.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes((ROOT / "packaging/litellm-core/pyproject.toml").read_bytes())
    (source / ".gitignore").write_text("*.cfg\n!keep.cfg\nbuild-artifacts/\n")
    (source / "litellm/.gitignore").write_text(".env\n")
    (source / ".git/info/exclude").write_text("litellm/private-local.json\n")
    (source / "litellm/private-local.json").write_text("synthetic packaging canary")
    for name in ("tracked.cfg", "local secret.cfg", "keep.cfg", ".env"):
        (source / "litellm" / name).write_text("synthetic packaging canary")
    (source / "litellm/build-artifacts").mkdir()
    (source / "litellm/build-artifacts/local.txt").write_text("generated artifact")
    subprocess.run(["git", "add", "--force", "litellm/tracked.cfg"], cwd=source, check=True)
    stage: Final = tmp_path / "stage"
    stage_core_distribution(source, stage)
    assert (stage / "litellm/keep.cfg").read_text() == "synthetic packaging canary"
    assert (stage / "litellm/shared.txt").read_text() == "shared payload"
    assert not (stage / "litellm/tracked.cfg").exists()
    assert not (stage / "litellm/local secret.cfg").exists()
    assert not (stage / "litellm/.env").exists()
    assert not (stage / "litellm/private-local.json").exists()
    assert not (stage / "litellm/build-artifacts").exists()
    assert (source / "litellm/tracked.cfg").is_file()


def test_staging_rejects_missing_release_version(tmp_path: Path) -> None:
    from scripts.build_core_distribution import stage_core_distribution

    manifest: Final = tmp_path / "packaging/litellm-core/pyproject.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes((ROOT / "packaging/litellm-core/pyproject.toml").read_bytes())
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "litellm"\n')
    with pytest.raises(subprocess.CalledProcessError):
        stage_core_distribution(tmp_path, tmp_path / "stage")
    assert not (tmp_path / "stage").exists()


def test_core_wheel_and_companion_import_without_repository(distribution_directory: Path, tmp_path: Path) -> None:
    wheels: Final = tuple(distribution_directory.glob("litellm_core-*.whl"))
    companions: Final = tuple(distribution_directory.glob("staticduo_litellm-*.whl"))
    assert len(wheels) == len(companions) == 1
    environment: Final = tmp_path / "installed"
    subprocess.run(["uv", "venv", "--python", sys.executable, str(environment)], check=True)
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(environment),
            "--find-links",
            str(distribution_directory),
            str(wheels[0]),
            str(companions[0]),
        ],
        check=True,
    )
    python: Final = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    probe: Final = """
import importlib.util
from importlib.metadata import version
import litellm
from staticduo_litellm.pricing.catalog import apply_catalog_overlay
assert version("staticduo-litellm") == "0.1.0"
assert all(importlib.util.find_spec(module) is None for module in ("fastapi", "mcp", "redis"))
assert apply_catalog_overlay(litellm.model_cost) == litellm.model_cost
response = litellm.completion(model="gpt-4o", messages=[{"role":"user","content":"fixture"}], mock_response="pong")
assert response.choices[0].message.content == "pong"
print("installed core and companion wheel OK")
"""
    result: Final = subprocess.run(
        [str(python), "-I", "-c", probe],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "LITELLM_LOCAL_MODEL_COST_MAP": "True"},
        check=True,
    )
    assert result.stdout.strip() == "installed core and companion wheel OK"
