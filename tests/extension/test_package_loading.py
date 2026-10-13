"""Build and install the extension without a source checkout or LiteLLM."""

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def test_wheel_contains_policies_and_runs_without_litellm(tmp_path: Path):
    root = Path(__file__).resolve().parents[2]
    uv = ["uvx", "--from", "uv==0.11.26", "uv"]
    environment = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(tmp_path / "venv")}
    subprocess.run(
        [*uv, "build", "--package", "staticduo-litellm", "--wheel", "--out-dir", str(tmp_path / "wheels")],
        cwd=root,
        env=environment,
        check=True,
    )
    wheel = next((tmp_path / "wheels").glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        packaged = frozenset(archive.namelist())
        source = root / "extensions/staticduo-litellm/src"
        modules = frozenset(
            path.relative_to(source).as_posix()
            for path in (source / "staticduo_litellm").rglob("*")
            if path.is_file() and path.suffix in (".py", ".json")
        )
        assert modules <= packaged
        metadata = archive.read("staticduo_litellm-0.1.0.dist-info/METADATA").decode()
        assert "Requires-Dist: litellm" not in metadata
    subprocess.run(
        [
            *uv,
            "sync",
            "--frozen",
            "--package",
            "staticduo-litellm",
            "--no-default-groups",
            "--no-install-package",
            "staticduo-litellm",
        ],
        cwd=root,
        env=environment,
        check=True,
    )
    python = tmp_path / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run([*uv, "pip", "install", "--python", str(python), "--no-deps", str(wheel)], check=True)
    probe = """
import asyncio
import importlib.util
from importlib.metadata import version
from staticduo_litellm.codex.portable import PortableTransportError, transform_request
from staticduo_litellm.pricing.catalog import apply_catalog_overlay, load_catalog_overlay

assert importlib.util.find_spec("litellm") is None
assert version("staticduo-litellm") == "0.1.0"
assert all(importlib.util.find_spec(module) is None for module in ("fastapi", "redis", "mcp"))
assert load_catalog_overlay()["schema_version"] == 1
catalog = apply_catalog_overlay({})
assert catalog and apply_catalog_overlay(catalog) == catalog

class Store:
    async def contains(self, key): return False
    async def record(self, key): pass
    async def get_mode(self, key): return None
    async def claim_mode(self, key, mode): return mode

request, context = asyncio.run(transform_request({"input": [{"type": "agent_message", "author": "root", "recipient": "child", "content": "fixture"}]}, "owner", Store()))
assert request["input"][0]["role"] == "user"
assert request["input"][0]["content"][1]["text"] == "fixture"
assert context.owner == "owner"
try:
    asyncio.run(transform_request({"previous_response_id": "unsupported"}, "owner", Store()))
except PortableTransportError as error:
    assert error.status_code == 400
else:
    raise AssertionError("history invariant was not enforced")
print("standalone wheel policy OK")
"""
    result = subprocess.run([str(python), "-I", "-c", probe], cwd=tmp_path, capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "standalone wheel policy OK"
