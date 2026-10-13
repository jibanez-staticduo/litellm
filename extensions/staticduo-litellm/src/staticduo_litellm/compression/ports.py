from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal, Protocol


class CompressionResult(Protocol):
    @property
    def messages(self) -> Sequence[Mapping[str, object]]: ...

    @property
    def succeeded(self) -> bool: ...

    @property
    def stats(self) -> Mapping[str, object]: ...

    @property
    def ccr_hashes(self) -> frozenset[str]: ...


class NativeCompressionPorts(Protocol):
    @property
    def model(self) -> str | None: ...

    @property
    def ccr_retrieval(self) -> bool: ...

    @property
    def skip_tool(self) -> bool: ...

    @property
    def only_tool(self) -> bool: ...

    def should_bypass(self, request_data: Mapping[str, object]) -> bool: ...

    async def compress(self, messages: Sequence[Mapping[str, object]], model: str | None) -> CompressionResult: ...

    def handle_failure(
        self, messages: Sequence[Mapping[str, object]], message: str, details: Mapping[str, object]
    ) -> object: ...

    def retrieve_tool(self) -> Mapping[str, object]: ...

    def retrieve_function(self) -> Mapping[str, object]: ...

    def resolve_call_id(self, request_data: Mapping[str, object]) -> str | None: ...

    def remember_hashes(self, call_id: str, hashes: frozenset[str]) -> None: ...

    def mark_applied(
        self,
        request_data: dict[str, object],  # mutable-ok: upstream logging out-param
    ) -> None: ...

    def record(
        self,
        guardrail_json_response: Mapping[str, object],
        request_data: dict[str, object],  # mutable-ok: upstream logging updates the handler request
        guardrail_status: Literal["success", "guardrail_failed_to_respond"],
        start_time: float,
        end_time: float,
    ) -> None: ...
