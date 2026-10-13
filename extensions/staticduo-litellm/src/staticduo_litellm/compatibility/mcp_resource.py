from starlette.requests import Request

from litellm.proxy._experimental.mcp_server.oauth_utils import get_request_base_url
from litellm.proxy.auth.ip_address_utils import IPAddressUtils

__all__ = ["get_request_base_url", "is_request_from_trusted_proxy"]


def is_request_from_trusted_proxy(request: Request) -> bool:
    return IPAddressUtils.is_request_from_trusted_proxy(request)
