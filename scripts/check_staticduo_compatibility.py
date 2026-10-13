"""Check source, upstream OAuth, installed ABI and release wheel contracts."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
from email.parser import BytesParser
from pathlib import Path
from typing import Final

import tomllib
from pydantic import BaseModel, ConfigDict, Field

# Source checkout CLI; runtime checks still use distribution metadata and actual imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extensions/staticduo-litellm/src"))
from staticduo_litellm.compatibility.provider_upstream import check_provider_upstream_source
from staticduo_litellm.compatibility.release_manifest import (
    CompatibilityError,
    FrozenContract,
    ReleaseContract,
    RuntimeEvidence,
    check_interfaces,
    check_versions,
)

MANIFEST_PATH: Final = "extensions/staticduo-litellm/src/staticduo_litellm/compatibility/release-manifest.json"


class WheelReceipt(FrozenContract):
    path: str
    sha256: str


class CandidateValidation(FrozenContract):
    schema_version: int = 1
    candidate_revision: str
    worktree: bool
    upstream_revision: str
    extension_version: str
    core_version: str
    compatibility_manifest_sha256: str
    manifest: ReleaseContract = Field(exclude=True)


class ProjectVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: str


class ProjectDocument(BaseModel):
    model_config = ConfigDict(frozen=True)
    project: ProjectVersion


class LockedPackage(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    version: str


class WorkspaceLock(BaseModel):
    model_config = ConfigDict(frozen=True)
    package: tuple[LockedPackage, ...]


class NativeBuildBinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    sha256: str


class BuildBinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    compatibility_manifest_sha256: str
    source_core_sha: str
    native: NativeBuildBinding


class RuntimeRequest(FrozenContract):
    manifest: ReleaseContract
    native_sha256: str | None


class GateEvidence(FrozenContract):
    candidate: CandidateValidation
    runtime: RuntimeEvidence | None
    wheel: WheelReceipt | None


class GateArguments(argparse.Namespace):
    repo: Path
    upstream_ref: str
    candidate_ref: str | None
    runtime: bool
    build_manifest: Path | None
    wheel: Path | None


def git(repo: Path, *arguments: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *arguments], check=True, capture_output=True).stdout


def resolve(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def check_wheel(wheel: Path, manifest: ReleaseContract) -> WheelReceipt:
    with zipfile.ZipFile(wheel) as archive:
        names: Final = tuple(archive.namelist())
        metadata_paths: Final = tuple(name for name in names if name.endswith(".dist-info/METADATA"))
        if len(metadata_paths) != 1:
            raise CompatibilityError("Wheel distribution metadata is missing or ambiguous")
        metadata: Final = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if metadata["Name"] != "staticduo-litellm" or metadata["Version"] != manifest.extension_version:
            raise CompatibilityError("Wheel distribution/version mismatch")
        expected: Final = (
            *tuple(path.removeprefix("extensions/staticduo-litellm/src/") for path in manifest.required_files),
            "staticduo_litellm/compatibility/release-manifest.json",
        )
        if not set(expected) <= set(names):
            raise CompatibilityError("Wheel is missing extension modules/data/manifest")
        packaged: Final = ReleaseContract.model_validate_json(archive.read(expected[-1]))
        if packaged != manifest:
            raise CompatibilityError("Wheel compatibility manifest differs from candidate")
    return WheelReceipt(path=wheel.name, sha256=hashlib.sha256(wheel.read_bytes()).hexdigest())


def check_candidate(repo: Path, upstream_ref: str, candidate_ref: str | None = None) -> CandidateValidation:
    upstream: Final = resolve(repo, upstream_ref)
    candidate: Final = resolve(repo, candidate_ref) if candidate_ref else None

    def read(path: str) -> bytes:
        return git(repo, "show", f"{candidate}:{path}") if candidate else (repo / path).read_bytes()

    manifest_bytes: Final = read(MANIFEST_PATH)
    manifest: Final = ReleaseContract.model_validate_json(manifest_bytes)
    if manifest.schema_version != 1:
        raise CompatibilityError("Unsupported compatibility schema")
    baseline: Final = resolve(repo, manifest.upstream_baseline_commit)
    subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, upstream], check=True, capture_output=True
    )
    provider: Final = manifest.provider_upstream
    historical: Final = git(repo, "show", f"{baseline}:{provider.path}")
    if hashlib.sha256(historical).hexdigest() != provider.sha256:
        raise CompatibilityError("Provider source hash lacks declared historical provenance")
    fresh: Final = git(repo, "show", f"{upstream}:{provider.path}")
    check_provider_upstream_source(fresh)
    if hashlib.sha256(fresh).hexdigest() != provider.sha256:
        raise CompatibilityError("Candidate provider contract differs from upstream contract")
    core: Final = ProjectDocument.model_validate(tomllib.loads(read("pyproject.toml").decode())).project.version
    extension: Final = ProjectDocument.model_validate(
        tomllib.loads(read("extensions/staticduo-litellm/pyproject.toml").decode())
    ).project.version
    check_versions(manifest, {"litellm": core, "staticduo-litellm": extension})
    check_interfaces(manifest, read)
    lock: Final = WorkspaceLock.model_validate(tomllib.loads(read("uv.lock").decode()))
    versions: Final = {
        item.name: item.version for item in lock.package if item.name in ("litellm", "staticduo-litellm")
    }
    if versions != {"litellm": core, "staticduo-litellm": extension}:
        raise CompatibilityError("Frozen workspace lock does not bind core and extension versions")
    return CandidateValidation(
        candidate_revision=candidate or resolve(repo, "HEAD"),
        worktree=candidate is None,
        upstream_revision=upstream,
        extension_version=extension,
        core_version=core,
        compatibility_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        manifest=manifest,
    )


def main() -> None:
    parser: Final = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--upstream-ref", required=True)
    parser.add_argument("--candidate-ref", help="Omit to validate the working tree")
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--build-manifest", type=Path, help="Verify installed native binary against build receipt")
    parser.add_argument("--wheel", type=Path)
    args: Final = GateArguments()
    parser.parse_args(namespace=args)
    try:
        result: Final = check_candidate(args.repo, args.upstream_ref, args.candidate_ref)
        manifest: Final = result.manifest
        runtime_evidence: RuntimeEvidence | None = None  # rebind-ok: optional CLI checks populate this evidence
        wheel_evidence: WheelReceipt | None = None  # rebind-ok: optional CLI checks populate this evidence
        if args.runtime:
            native_hash = None  # rebind-ok: optional CLI runtime/wheel checks determine this evidence
            if args.build_manifest:
                build: Final = BuildBinding.model_validate_json(args.build_manifest.read_text())
                if (
                    build.compatibility_manifest_sha256 != result.compatibility_manifest_sha256
                    or build.source_core_sha != result.candidate_revision
                ):
                    raise CompatibilityError("Build receipt does not bind the checked candidate")
                native_hash = build.native.sha256  # rebind-ok: optional build receipt
                if not re.fullmatch(r"[0-9a-f]{64}", native_hash):
                    raise CompatibilityError("Native build hash is invalid")
            probe: Final = """
import json, sys
from importlib.metadata import distribution
from staticduo_litellm.compatibility.release_manifest import ReleaseContract, check_runtime, load_manifest
request = json.load(sys.stdin)
expected = ReleaseContract.model_validate(request["manifest"])
for name in ("litellm", "staticduo-litellm"):
    raw = distribution(name).read_text("direct_url.json")
    if raw and json.loads(raw).get("dir_info", {}).get("editable"):
        raise RuntimeError("Release runtime requires wheel installations, not editable checkouts")
if load_manifest() != expected:
    raise RuntimeError("Installed extension manifest differs from checked candidate")
result = check_runtime(expected, expected_native_sha256=request["native_sha256"])
sys.stdout.write(result.model_dump_json())
"""
            runtime: Final = subprocess.run(
                [sys.executable, "-I", "-c", probe],
                input=RuntimeRequest(manifest=manifest, native_sha256=native_hash).model_dump_json(),
                text=True,
                capture_output=True,
                check=False,
            )
            if runtime.returncode:
                raise CompatibilityError("Installed runtime compatibility failed: " + runtime.stderr.strip())
            runtime_evidence = RuntimeEvidence.model_validate_json(runtime.stdout)  # rebind-ok: optional probe
        if args.wheel:
            wheel_evidence = check_wheel(args.wheel, manifest)  # rebind-ok: optional wheel
    except (CompatibilityError, RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Compatibility gate failed: {error}\n")
    sys.stdout.write(
        GateEvidence(candidate=result, runtime=runtime_evidence, wheel=wheel_evidence).model_dump_json(indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
