from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

from litellm.images.utils import ImageEditRequestUtils
from litellm.llms.chatgpt.common_utils import without_oauth_identity_headers
from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig
from litellm.llms.openai.image_edit.transformation import OpenAIImageEditConfig
from litellm.llms.openai.image_generation.gpt_transformation import GPTImageGenerationConfig
from litellm.types.llms.openai import AllMessageValues, FileTypes
from litellm.types.router import GenericLiteLLMParams

__all__: Final = (
    "AllMessageValues",
    "ChatGPTResponsesAPIConfig",
    "FileTypes",
    "GPTImageGenerationConfig",
    "GenericLiteLLMParams",
    "ImageEditRequestUtils",
    "OpenAIImageEditConfig",
    "without_oauth_identity_headers",
)
