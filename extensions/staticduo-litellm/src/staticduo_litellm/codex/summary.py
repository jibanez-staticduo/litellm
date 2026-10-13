from typing import Final

"""Public entry point with ordered initialization of the LiteLLM runtime."""

from importlib import import_module

# Core facades load the implementation directly while LiteLLM initializes.
import_module("litellm")
from staticduo_litellm.codex.summary_runtime import (
    SUMMARY_BUFFER_MAX_BYTES,
    SUMMARY_BUFFER_MAX_EVENTS,
    SUMMARY_INSTRUCTIONS,
    SUMMARY_TIMEOUT_SECONDS,
    EventView,
    HostedVLLMCodexSummaryStream,
    SummaryStream,
    T,
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
    "EventView",
    "HostedVLLMCodexSummaryStream",
    "SummaryStream",
    "T",
    "apply_summary",
    "generate_summary",
    "run_summary_sync",
    "summarize_response",
    "summary_args",
    "summary_requested",
)
