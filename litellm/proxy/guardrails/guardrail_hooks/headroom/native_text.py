"""Compatibility exports for native Headroom text handling."""

from staticduo_litellm.compression.native_text import (
    NativeRequestFormat,
    NativeTextSlot,
    TextPath,
    extract_native_text_slots,
    has_native_retrieve_tool,
    patch_native_text_slots,
)

__all__ = [
    "NativeRequestFormat",
    "NativeTextSlot",
    "TextPath",
    "extract_native_text_slots",
    "has_native_retrieve_tool",
    "patch_native_text_slots",
]
