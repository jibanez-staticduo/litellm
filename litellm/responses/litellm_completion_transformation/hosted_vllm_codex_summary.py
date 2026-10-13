from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.codex.summary_runtime import (
    _SUMMARY_CAPACITY,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SYNC_LOOP_LOCK,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _USAGE_ADAPTER,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    SUMMARY_BUFFER_MAX_BYTES,
    SUMMARY_BUFFER_MAX_EVENTS,
    SUMMARY_INSTRUCTIONS,
    SUMMARY_TIMEOUT_SECONDS,
    EventView,
    HostedVLLMCodexSummaryStream,
    SummaryStream,
    T,
    _SummaryMergeState,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _sync_loop_state,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SyncLoopState,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    apply_summary,
    generate_summary,
    run_summary_sync,
    summarize_response,
    summary_args,
    summary_requested,
)

__all__: Final = (
    "SUMMARY_BUFFER_MAX_BYTES",
    "SUMMARY_BUFFER_MAX_EVENTS",
    "SUMMARY_INSTRUCTIONS",
    "SUMMARY_TIMEOUT_SECONDS",
    "_SUMMARY_CAPACITY",
    "_SYNC_LOOP_LOCK",
    "_USAGE_ADAPTER",
    "EventView",
    "HostedVLLMCodexSummaryStream",
    "SummaryStream",
    "T",
    "_SummaryMergeState",
    "_SyncLoopState",
    "_sync_loop_state",
    "apply_summary",
    "generate_summary",
    "run_summary_sync",
    "summarize_response",
    "summary_args",
    "summary_requested",
)
