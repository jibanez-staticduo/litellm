from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.codex.reasoning_content import (
    normalize_reasoning_content,
    should_normalize_reasoning_content,
)

__all__: Final = ("normalize_reasoning_content", "should_normalize_reasoning_content")
