from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.codex.tool_search import (
    _ARGUMENTS_ADAPTER,
    _TOOLS_ADAPTER,
    TOOL_SEARCH_NAME,
    build_tool_search_call,
    has_client_tool_search,
    merge_discovered_tools,
)

__all__: Final = ('TOOL_SEARCH_NAME', '_ARGUMENTS_ADAPTER', '_TOOLS_ADAPTER', 'build_tool_search_call', 'has_client_tool_search', 'merge_discovered_tools')
