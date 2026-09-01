from __future__ import annotations

import os
import re
from ipaddress import ip_address
from typing import Final, Literal, TypeAlias
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict
from starlette.requests import Request
from starlette.types import Scope

from litellm.proxy._experimental.mcp_server.oauth_utils import get_request_base_url
from litellm.proxy.auth.ip_address_utils import IPAddressUtils

LazyMcpResourceKind = Literal["aggregate", "scope", "toolset"]
_IDENTIFIER: Final = re.compile(r"^[A-Za-z0-9._~-]+$")


class LazyMcpPublicResource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: LazyMcpResourceKind
    identifier: str | None
    canonical_uri: str
    transport_path: str
    metadata_path: str


class LazyMcpResourceError(BaseModel):
    model_config = ConfigDict(frozen=True)

    tag: Literal["invalid_lazymcp_resource"] = "invalid_lazymcp_resource"


LazyMcpResourceResult: TypeAlias = LazyMcpPublicResource | LazyMcpResourceError


def _valid_identifier(identifier: str) -> bool:
    return identifier not in (".", "..") and _IDENTIFIER.fullmatch(identifier) is not None


def _is_loopback_host(hostname: str) -> bool:
    if hostname == "localhost":
        return True
    try:
        return ip_address(hostname).is_loopback
    except ValueError:
        return False


def _request_peer_is_loopback(request: Request) -> bool:
    client: Final = request.client
    return client is not None and _is_loopback_host(client.host)


def _configured_base_is_valid(configured: str) -> bool:
    try:
        parsed: Final = urlsplit(configured)
    except ValueError:
        return False
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
        and not parsed.query
        and not parsed.fragment
        and "%" not in parsed.path
        and "\\" not in parsed.path
    )


def _transport_identity(path: str) -> tuple[LazyMcpResourceKind, str | None, str] | None:
    canonical_path: Final = path[:-1] if path.endswith("/") and path != "/" else path
    if canonical_path == "/lazymcp":
        return "aggregate", None, canonical_path
    scope_match: Final = re.fullmatch(r"/lazymcp/([^/]+)", canonical_path)
    if scope_match is not None and _valid_identifier(scope_match.group(1)):
        return "scope", scope_match.group(1), canonical_path
    toolset_match: Final = re.fullmatch(r"/toolset/([^/]+)/lazymcp", canonical_path)
    if toolset_match is not None and _valid_identifier(toolset_match.group(1)):
        return "toolset", toolset_match.group(1), canonical_path
    return None


def _trusted_base(request: Request) -> tuple[str, str] | None:
    configured: Final = os.environ.get("PROXY_BASE_URL", "").strip()
    if configured and not _configured_base_is_valid(configured):
        return None
    base: Final = get_request_base_url(request)
    try:
        parsed: Final = urlsplit(base)
        hostname: Final = parsed.hostname or ""
    except ValueError:
        return None
    loopback: Final = _is_loopback_host(hostname)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password:
        return None
    if parsed.query or parsed.fragment or "%" in parsed.path or "\\" in parsed.path:
        return None
    configured_base: Final = bool(configured)
    trusted_proxy: Final = IPAddressUtils.is_request_from_trusted_proxy(request)
    peer_loopback: Final = _request_peer_is_loopback(request)
    if not configured_base and not trusted_proxy and not (loopback and peer_loopback):
        return None
    if parsed.scheme != "https" and not (loopback and peer_loopback):
        return None
    root: Final = parsed.path.rstrip("/")
    origin: Final = f"{parsed.scheme}://{parsed.netloc}"
    return origin, root


def _build_resource(request: Request, transport_path: str) -> LazyMcpResourceResult:
    trusted: Final = _trusted_base(request)
    identity: Final = _transport_identity(transport_path)
    if trusted is None or identity is None:
        return LazyMcpResourceError()
    origin, root = trusted
    kind, identifier, canonical_path = identity
    return LazyMcpPublicResource(
        kind=kind,
        identifier=identifier,
        canonical_uri=f"{origin}{root}{canonical_path}",
        transport_path=canonical_path,
        metadata_path=f"/.well-known/oauth-protected-resource{root}{canonical_path}",
    )


def parse_lazymcp_resource(request: Request, candidate: str) -> LazyMcpResourceResult:
    if not candidate or not candidate.isascii() or "%" in candidate or "\\" in candidate:
        return LazyMcpResourceError()
    try:
        parsed: Final = urlsplit(candidate)
    except ValueError:
        return LazyMcpResourceError()
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        return LazyMcpResourceError()
    trusted: Final = _trusted_base(request)
    if trusted is None:
        return LazyMcpResourceError()
    origin, root = trusted
    if f"{parsed.scheme}://{parsed.netloc}" != origin or not parsed.path.startswith(f"{root}/"):
        return LazyMcpResourceError()
    resource: Final = _build_resource(request, parsed.path[len(root) :])
    if not isinstance(resource, LazyMcpPublicResource):
        return resource
    canonical_candidate: Final = candidate.removesuffix("/")
    if canonical_candidate != resource.canonical_uri:
        return LazyMcpResourceError()
    return resource


def resource_from_transport_scope(scope: Scope) -> LazyMcpResourceResult:
    request: Final = Request(scope)
    path: Final = str(scope.get("_original_path") or scope.get("path") or "")
    trusted: Final = _trusted_base(request)
    if trusted is None:
        return LazyMcpResourceError()
    _, root = trusted
    transport_path: Final = path[len(root) :] if root and path.startswith(f"{root}/") else path
    return _build_resource(request, transport_path)


def build_lazymcp_metadata(resource: LazyMcpPublicResource, authorization_server: str) -> dict[str, object]:
    return {"resource": resource.canonical_uri, "authorization_servers": [authorization_server]}


def build_lazymcp_challenge(resource: LazyMcpPublicResource, invalid_token: bool) -> str:
    parsed: Final = urlsplit(resource.canonical_uri)
    metadata_url: Final = f"{parsed.scheme}://{parsed.netloc}{resource.metadata_path}"
    error: Final = 'error="invalid_token", ' if invalid_token else ""
    return f'Bearer {error}resource_metadata="{metadata_url}"'


def is_lazymcp_resource_candidate(request: Request, candidate: str) -> bool:
    try:
        path: Final = unquote(urlsplit(candidate).path).lower()
    except (UnicodeDecodeError, ValueError):
        return False
    trusted: Final = _trusted_base(request)
    root: Final = trusted[1].lower() if trusted is not None else ""
    if root and not path.startswith(f"{root}/"):
        return False
    relative_path: Final = path[len(root) :] if root else path
    segments: Final = relative_path.strip("/").split("/") if relative_path.strip("/") else []
    return bool(
        segments
        and (
            (segments[0] == "lazymcp" and len(segments) in (1, 2))
            or (len(segments) == 3 and segments[0] == "toolset" and segments[2] == "lazymcp")
        )
    )
