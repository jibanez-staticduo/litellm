"""Packaged-runtime regression for LazyMCP discovery origin trust.

The shipped proxy must derive OAuth metadata from an explicit trusted public
base when a non-loopback container peer reaches it over internal HTTP. OpenAPI
route declarations alone do not prove that request-time trust checks pass.

Gated on LITELLM_IMAGE so normal source test runs skip it. Requires a working
Docker CLI and exercises the image's normal entrypoint.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Final, cast

import pytest

IMAGE: Final = os.getenv("LITELLM_IMAGE")
CURL_IMAGE: Final = os.getenv("LITELLM_TEST_CURL_IMAGE", "curlimages/curl:8.11.1")
PROXY_PORT: Final = os.getenv("LITELLM_IMAGE_PROXY_PORT", "4000")
STARTUP_TIMEOUT_SECONDS: Final = int(os.getenv("LITELLM_IMAGE_STARTUP_TIMEOUT", "180"))
TRUSTED_PUBLIC_BASE: Final = "https://candidate.invalid"
GENERIC_NOT_FOUND: Final = {"detail": "Not Found"}
JSON_CONTENT_TYPE: Final = "application/json"
DISCOVERY_CASES: Final = (
    (
        "/.well-known/oauth-protected-resource/lazymcp",
        f"{TRUSTED_PUBLIC_BASE}/lazymcp",
    ),
    (
        "/lazymcp/.well-known/oauth-protected-resource",
        f"{TRUSTED_PUBLIC_BASE}/lazymcp",
    ),
    (
        "/.well-known/oauth-protected-resource/lazymcp/team-a",
        f"{TRUSTED_PUBLIC_BASE}/lazymcp/team-a",
    ),
    (
        "/lazymcp/team-a/.well-known/oauth-protected-resource",
        f"{TRUSTED_PUBLIC_BASE}/lazymcp/team-a",
    ),
    (
        "/.well-known/oauth-protected-resource/toolset/tools-a/lazymcp",
        f"{TRUSTED_PUBLIC_BASE}/toolset/tools-a/lazymcp",
    ),
    (
        "/toolset/tools-a/lazymcp/.well-known/oauth-protected-resource",
        f"{TRUSTED_PUBLIC_BASE}/toolset/tools-a/lazymcp",
    ),
)
DISCOVERY_TEMPLATES: Final = frozenset(
    {
        "/.well-known/oauth-protected-resource/lazymcp",
        "/.well-known/oauth-protected-resource/lazymcp/{scope}",
        "/.well-known/oauth-protected-resource/toolset/{name}/lazymcp",
        "/lazymcp/.well-known/oauth-protected-resource",
        "/lazymcp/{scope}/.well-known/oauth-protected-resource",
        "/toolset/{name}/lazymcp/.well-known/oauth-protected-resource",
    }
)

pytestmark = [
    pytest.mark.skipif(IMAGE is None, reason="requires a built image (set LITELLM_IMAGE)"),
    pytest.mark.skipif(shutil.which("docker") is None, reason="requires the docker CLI"),
]


@dataclass(frozen=True, slots=True)
class ImageProxy:
    network: str
    container: str


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status_code: int
    content_type: str
    body: str

    def json(self) -> object:
        return cast(object, json.loads(self.body))


def _string_keyed_object_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        pytest.fail(f"expected a JSON object with string keys, got {value!r}")
    raw: Final = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in raw):
        pytest.fail(f"expected a JSON object with string keys, got {value!r}")
    return cast(dict[str, object], raw)


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check)


def _container_logs(container: str) -> str:
    logs: Final = _docker("logs", container, check=False)
    return f"stdout:\n{logs.stdout}\nstderr:\n{logs.stderr}"


def _is_running(container: str) -> bool:
    result: Final = _docker(
        "ps",
        "--filter",
        f"name=^/{container}$",
        "--filter",
        "status=running",
        "--format",
        "{{.Names}}",
        check=False,
    )
    return result.stdout.strip() == container


def _request(proxy: ImageProxy, path: str, *, fail_on_transport_error: bool = True) -> HttpResponse | None:
    result: Final = _docker(
        "run",
        "--rm",
        "--network",
        proxy.network,
        CURL_IMAGE,
        "--silent",
        "--show-error",
        "--max-time",
        "10",
        "--output",
        "-",
        "--write-out",
        "\n%{http_code}\n%{content_type}",
        f"http://{proxy.container}:{PROXY_PORT}{path}",
        check=False,
    )
    if result.returncode != 0:
        if not fail_on_transport_error:
            return None
        pytest.fail(
            f"GET {path} failed with curl exit {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}\n"
            f"{_container_logs(proxy.container)}"
        )
    body_and_status, content_type_separator, content_type = result.stdout.rpartition("\n")
    body, status_separator, status = body_and_status.rpartition("\n")
    if not content_type_separator or not status_separator or not status.isdigit():
        pytest.fail(f"GET {path} returned an invalid probe response: {result.stdout!r}")
    return HttpResponse(status_code=int(status), content_type=content_type, body=body)


def _wait_until_ready(proxy: ImageProxy) -> None:
    deadline: Final = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if not _is_running(proxy.container):
            pytest.fail(f"the packaged proxy exited during startup\n{_container_logs(proxy.container)}")
        response = _request(proxy, "/health/liveliness", fail_on_transport_error=False)
        if response is not None and response.status_code == 200:
            return
        time.sleep(2)
    pytest.fail(
        f"the packaged proxy did not become live within {STARTUP_TIMEOUT_SECONDS}s\n{_container_logs(proxy.container)}"
    )


def _start_proxy(environment: Mapping[str, str]) -> Iterator[ImageProxy]:
    run_id: Final = f"lazymcp-image-{uuid.uuid4().hex[:8]}"
    network: Final = f"{run_id}-net"
    container: Final = f"{run_id}-app"
    environment_args: Final = tuple(
        argument for name, value in environment.items() for argument in ("-e", f"{name}={value}")
    )
    _docker("network", "create", "--internal", network)
    try:
        assert IMAGE is not None
        _docker(
            "run",
            "-d",
            "--name",
            container,
            "--network",
            network,
            "-e",
            "LITELLM_LOCAL_MODEL_COST_MAP=True",
            *environment_args,
            IMAGE,
        )
        proxy: Final = ImageProxy(network=network, container=container)
        _wait_until_ready(proxy)
        yield proxy
    finally:
        _docker("logs", container, check=False)
        _docker("rm", "-f", container, check=False)
        _docker("network", "rm", network, check=False)


@pytest.fixture(scope="module", autouse=True)
def pull_curl_image() -> None:
    _docker("pull", "--quiet", CURL_IMAGE)


@pytest.fixture
def unset_proxy() -> Iterator[ImageProxy]:
    yield from _start_proxy({})


@pytest.fixture
def non_loopback_http_proxy() -> Iterator[ImageProxy]:
    yield from _start_proxy({"PROXY_BASE_URL": "http://candidate.invalid"})


@pytest.fixture(scope="module")
def trusted_proxy() -> Iterator[ImageProxy]:
    yield from _start_proxy({"PROXY_BASE_URL": TRUSTED_PUBLIC_BASE})


def _assert_all_discovery_aliases_return_generic_404(proxy: ImageProxy) -> None:
    for path, _resource in DISCOVERY_CASES:
        response = _request(proxy, path)
        assert response is not None
        assert response.status_code == 404, f"GET {path} returned {response.status_code}: {response.body}"
        assert response.content_type == JSON_CONTENT_TYPE
        assert response.json() == GENERIC_NOT_FOUND


def test_non_loopback_peer_with_unset_public_base_gets_generic_404(unset_proxy: ImageProxy) -> None:
    _assert_all_discovery_aliases_return_generic_404(unset_proxy)


def test_non_loopback_http_public_base_gets_generic_404(non_loopback_http_proxy: ImageProxy) -> None:
    _assert_all_discovery_aliases_return_generic_404(non_loopback_http_proxy)


def test_trusted_https_base_returns_exact_metadata_for_all_six_aliases(trusted_proxy: ImageProxy) -> None:
    for path, resource in DISCOVERY_CASES:
        response = _request(trusted_proxy, path)
        assert response is not None
        assert response.status_code == 200, f"GET {path} returned {response.status_code}: {response.body}"
        assert response.content_type == JSON_CONTENT_TYPE
        assert response.json() == {
            "resource": resource,
            "authorization_servers": [f"{TRUSTED_PUBLIC_BASE}/mcp"],
        }


def test_packaged_openapi_contains_all_six_discovery_templates(trusted_proxy: ImageProxy) -> None:
    response: Final = _request(trusted_proxy, "/openapi.json")
    assert response is not None
    assert response.status_code == 200
    payload: Final = _string_keyed_object_dict(response.json())
    paths: Final = payload.get("paths")
    assert DISCOVERY_TEMPLATES <= _string_keyed_object_dict(paths).keys()
