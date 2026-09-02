from typing import Final

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import Response

from litellm._logging import verbose_proxy_logger

router: Final = APIRouter()
_METHODS: Final = ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD")


async def _forward_lazymcp(request: Request, internal_path: str) -> Response:
    from litellm.proxy import proxy_server
    from litellm.proxy._experimental.mcp_server.server import handle_streamable_http_lazymcp

    scope: Final = {  # mutable-ok: ASGI handlers require a mutable scope mapping
        **request.scope,
        "_original_path": request.scope.get("path", ""),
        "path": internal_path,
    }
    return await proxy_server._stream_mcp_asgi_response(handle_streamable_http_lazymcp, scope, request.receive)


@router.api_route("/lazymcp/", methods=_METHODS)
@router.api_route("/lazymcp", methods=_METHODS)
async def root_lazymcp_route(request: Request) -> Response:
    try:
        return await _forward_lazymcp(request, "/lazymcp")
    except HTTPException:
        raise
    except Exception as exc:
        verbose_proxy_logger.exception("Error handling root LazyMCP route: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.api_route("/lazymcp/{scope_name}/", methods=_METHODS)
@router.api_route("/lazymcp/{scope_name}", methods=_METHODS)
async def scoped_lazymcp_route(scope_name: str, request: Request) -> Response:
    from litellm.proxy._experimental.mcp_server.server import _mcp_active_lazymcp_scope_name

    token: Final = _mcp_active_lazymcp_scope_name.set(scope_name)
    try:
        return await _forward_lazymcp(request, f"/lazymcp/{scope_name}")
    except HTTPException:
        raise
    except Exception as exc:
        verbose_proxy_logger.exception("Error handling scoped LazyMCP route for %s: %s", scope_name, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    finally:
        _mcp_active_lazymcp_scope_name.reset(token)


@router.api_route("/toolset/{toolset_name}/lazymcp/", methods=_METHODS)
@router.api_route("/toolset/{toolset_name}/lazymcp", methods=_METHODS)
async def toolset_lazymcp_route(toolset_name: str, request: Request) -> Response:
    from litellm.proxy._experimental.mcp_server.server import _mcp_active_toolset_name

    token: Final = _mcp_active_toolset_name.set(toolset_name)
    try:
        return await _forward_lazymcp(request, "/lazymcp")
    except HTTPException:
        raise
    except Exception as exc:
        verbose_proxy_logger.exception("Error handling toolset LazyMCP route for %s: %s", toolset_name, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    finally:
        _mcp_active_toolset_name.reset(token)
