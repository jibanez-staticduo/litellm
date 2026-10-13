from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from litellm.llms.base_llm.guardrail_translation.utils import (
    effective_scan_only_tool_results_for_guardrail,
    effective_skip_tool_message_for_guardrail,
)
from litellm.proxy.common_utils.callback_utils import (
    add_guardrail_to_applied_guardrails_header,  # pyright: ignore[reportUnknownVariableType]  # upstream request out-param is unparameterized
)
from litellm.proxy.guardrails.guardrail_hooks.headroom.headroom import (
    _HASH_CACHE_TTL_SECONDS,  # pyright: ignore[reportPrivateUsage]  # compatibility seam reuses upstream retrieval lifetime
    _REQUEST_DATA_ADAPTER,  # pyright: ignore[reportPrivateUsage]  # compatibility seam validates the upstream tool schema
    _build_headroom_retrieve_tool,  # pyright: ignore[reportPrivateUsage]  # compatibility seam reuses upstream retrieval definition
    _resolve_call_id,  # pyright: ignore[reportPrivateUsage]  # compatibility seam preserves upstream call identity
)
from litellm.proxy.spend_tracking.compression_savings import HEADROOM_GUARDRAIL_PROVIDER
from staticduo_litellm.compression import native_request
from staticduo_litellm.compression.native_text import NativeRequestFormat
from staticduo_litellm.compression.ports import CompressionResult

if TYPE_CHECKING:
    from litellm.litellm_core_utils.litellm_logging import Logging as LiteLLMLoggingObj
    from litellm.proxy.guardrails.guardrail_hooks.headroom.headroom import HeadroomGuardrail


@dataclass(frozen=True)
class HeadroomNativePorts:
    guardrail: HeadroomGuardrail
    logging_obj: LiteLLMLoggingObj | None

    @property
    def model(self) -> str | None:
        return self.guardrail.headroom_model

    @property
    def ccr_retrieval(self) -> bool:
        return self.guardrail.ccr_retrieval

    @property
    def skip_tool(self) -> bool:
        return effective_skip_tool_message_for_guardrail(self.guardrail)

    @property
    def only_tool(self) -> bool:
        return effective_scan_only_tool_results_for_guardrail(self.guardrail)

    def should_bypass(self, request_data: Mapping[str, object]) -> bool:
        return self.guardrail._should_bypass(_REQUEST_DATA_ADAPTER.validate_python(request_data))  # pyright: ignore[reportPrivateUsage]  # upstream bypass policy

    async def compress(self, messages: Sequence[Mapping[str, object]], model: str | None) -> CompressionResult:
        return await self.guardrail._call_compress(messages=[dict(row) for row in messages], model=model)  # pyright: ignore[reportPrivateUsage]  # upstream bounded HTTP transport

    def handle_failure(
        self, messages: Sequence[Mapping[str, object]], message: str, details: Mapping[str, object]
    ) -> object:
        return self.guardrail._handle_compress_failure([dict(row) for row in messages], message, dict(details))  # pyright: ignore[reportPrivateUsage]  # upstream fail-open/closed behavior

    def retrieve_tool(self) -> Mapping[str, object]:
        return _build_headroom_retrieve_tool()

    def retrieve_function(self) -> Mapping[str, object]:
        return _REQUEST_DATA_ADAPTER.validate_python(self.retrieve_tool()["function"])

    def resolve_call_id(self, request_data: Mapping[str, object]) -> str | None:
        return _resolve_call_id(self.logging_obj, _REQUEST_DATA_ADAPTER.validate_python(request_data))

    def remember_hashes(self, call_id: str, hashes: frozenset[str]) -> None:
        self.guardrail._prune_expired_hashes()  # pyright: ignore[reportPrivateUsage]  # upstream retrieval cache lifecycle
        self.guardrail._issued_hashes_by_call_id[call_id] = (hashes, time.monotonic() + _HASH_CACHE_TTL_SECONDS)  # pyright: ignore[reportPrivateUsage]  # upstream agentic hook owns issued hashes

    def mark_applied(
        self,
        request_data: dict[str, object],  # mutable-ok: upstream logging out-param
    ) -> None:
        add_guardrail_to_applied_guardrails_header(
            request_data=request_data, guardrail_name=self.guardrail.guardrail_name
        )

    def record(
        self,
        guardrail_json_response: Mapping[str, object],
        request_data: dict[str, object],  # mutable-ok: upstream logging updates the handler request
        guardrail_status: Literal["success", "guardrail_failed_to_respond"],
        start_time: float,
        end_time: float,
    ) -> None:
        self.guardrail.add_standard_logging_guardrail_information_to_request_data(  # pyright: ignore[reportUnknownMemberType]  # upstream request out-param is unparameterized
            guardrail_json_response=guardrail_json_response,
            request_data=request_data,
            guardrail_status=guardrail_status,
            guardrail_provider=HEADROOM_GUARDRAIL_PROVIDER,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
        )


async def process_native_request(
    guardrail: HeadroomGuardrail,
    request_data: dict[str, object],  # mutable-ok: native handler request out-param
    request_format: NativeRequestFormat,
    logging_obj: LiteLLMLoggingObj | None = None,
) -> dict[str, object]:  # mutable-ok: returns the handler request out-param
    return await native_request.process_native_request(
        HeadroomNativePorts(guardrail, logging_obj), request_data, request_format
    )
