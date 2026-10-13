from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.chatgpt.realtime import (
    CallAccounting,
    ChatGPTRealtime,
    ChatGPTRealtimeHTTPConfig,
    accounts_for_call_usage,
    configured_realtime_headers,
    configured_realtime_query,
    realtime_call_headers,
    realtime_endpoint,
    realtime_headers,
)

__all__: Final = ('CallAccounting', 'ChatGPTRealtime', 'ChatGPTRealtimeHTTPConfig', 'accounts_for_call_usage', 'configured_realtime_headers', 'configured_realtime_query', 'realtime_call_headers', 'realtime_endpoint', 'realtime_headers')
