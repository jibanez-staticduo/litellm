from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.chatgpt.codex import (
    ChatGPTCallRouting,
    CodexRealtimeCall,
    CodexRealtimeOffer,
    CodexSidebandRequest,
    build_call_request,
    build_sideband_request,
    parse_call_response,
)

__all__: Final = ('ChatGPTCallRouting', 'CodexRealtimeCall', 'CodexRealtimeOffer', 'CodexSidebandRequest', 'build_call_request', 'build_sideband_request', 'parse_call_response')
