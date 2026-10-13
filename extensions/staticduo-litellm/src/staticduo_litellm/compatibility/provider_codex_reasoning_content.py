from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

from litellm.exceptions import BadRequestError
from litellm.types.llms.openai import AllMessageValues

__all__: Final = ("AllMessageValues", "BadRequestError")
