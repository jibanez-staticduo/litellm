from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

import litellm
from litellm._logging import verbose_logger
from litellm.responses.litellm_completion_transformation.streaming_iterator import (
    LiteLLMCompletionStreamingIterator,
)
from litellm.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from litellm.types.llms.openai import ResponseCompletedEvent, ResponsesAPIResponse, ResponsesAPIStreamingResponse
from litellm.types.utils import BaseLiteLLMOpenAIResponseObject, ModelResponseStream


async def summary_completion(
    **kwargs: object,  # kwargs-ok: preserves LiteLLM completion arguments at the compatibility boundary
) -> object:
    return await litellm.acompletion(**kwargs)


__all__: Final = (
    "BaseLiteLLMOpenAIResponseObject",
    "BaseResponsesAPIStreamingIterator",
    "LiteLLMCompletionStreamingIterator",
    "ModelResponseStream",
    "ResponseCompletedEvent",
    "ResponsesAPIResponse",
    "ResponsesAPIStreamingResponse",
    "verbose_logger",
)
