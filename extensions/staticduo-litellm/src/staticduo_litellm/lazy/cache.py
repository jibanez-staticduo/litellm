from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from staticduo_litellm.compatibility.mcp_types import UserAPIKeyAuth

    from .ports import MCPPorts


from .schema import hash_value


class CacheService:
    ports: MCPPorts

    def cache_scope(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: list[str] | None,  # mutable-ok: framework contract requires mutable request or response containers
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        client_ip: str | None,
    ) -> str:
        object_permission: Final = user_api_key_auth.object_permission if user_api_key_auth is not None else None
        normalized_raw_headers: Final = {key.lower(): value for key, value in (raw_headers or {}).items()}
        object_permission_payload: Final = (
            object_permission.model_dump(mode="json") if object_permission is not None else None
        )

        scope_payload: Final = {
            "api_key_hash": hash_value(getattr(user_api_key_auth, "api_key", None)),
            "user_id": getattr(user_api_key_auth, "user_id", None),
            "team_id": getattr(user_api_key_auth, "team_id", None),
            "mcp_servers": mcp_servers or [],
            "active_toolset": self.ports.active_toolset.get(),
            "client_ip": client_ip,
            "mcp_auth_header_hash": hash_value(mcp_auth_header),
            "mcp_server_auth_headers_hash": hash_value(mcp_server_auth_headers),
            "oauth2_headers_hash": hash_value(oauth2_headers),
            "header_mcp_servers": normalized_raw_headers.get("x-mcp-servers"),
            "header_mcp_access_groups": normalized_raw_headers.get("x-mcp-access-groups"),
            "raw_header_names": sorted(normalized_raw_headers.keys()),
            "raw_header_values_hash": hash_value(normalized_raw_headers),
            "object_permission": object_permission_payload,
        }
        encoded = json.dumps(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            scope_payload, sort_keys=True, default=str
        )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
