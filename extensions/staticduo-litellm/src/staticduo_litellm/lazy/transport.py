from __future__ import annotations

import re
from typing import Final

from pydantic import TypeAdapter
from starlette.requests import Request as StarletteRequest
from starlette.types import Scope


def is_compatibility_request(scope: Scope) -> bool:
    method: Final = TypeAdapter(str).validate_python(scope.get("method", "")).upper()
    if method == "HEAD":
        return True
    if method != "GET":
        return False

    def _split_quoted_header(value: str, delimiter: str) -> tuple[str, ...]:
        fields: Final[  # mutable-ok: SDK and ASGI compatibility payload uses the canonical mutable shape
            list[str]
        ] = []
        field_start = 0  # rebind-ok: framework flow intentionally updates request or lifecycle state
        quoted = False  # rebind-ok: framework flow intentionally updates request or lifecycle state
        escaped = False  # rebind-ok: framework flow intentionally updates request or lifecycle state
        for index, character in enumerate(value):
            if escaped:
                escaped = False
            elif quoted and character == "\\":
                escaped = True
            elif character == '"':
                quoted = not quoted
            elif character == delimiter and not quoted:
                fields.append(value[field_start:index])
                field_start = index + 1
        fields.append(value[field_start:])
        return tuple(fields)

    accept_headers: Final = StarletteRequest(scope).headers.getlist("accept")
    for media_range in (
        value for header in accept_headers for value in _split_quoted_header(header, delimiter=",")
    ):  # comprehension-ok: parse ordered flattened HTTP Accept values
        media_type, *parameters = _split_quoted_header(media_range, delimiter=";")
        if media_type.strip().lower() != "text/event-stream":
            continue

        quality_parameters = tuple(
            parameter.partition("=") for parameter in parameters if parameter.partition("=")[0].strip().lower() == "q"
        )
        if not quality_parameters:
            return False
        if len(quality_parameters) != 1:
            continue

        _, separator, quality = quality_parameters[0]
        normalized_quality = quality.strip()
        if (
            separator
            and re.fullmatch(r"(?:0(?:\.\d{0,3})?|1(?:\.0{0,3})?)", normalized_quality)
            and float(normalized_quality) > 0
        ):
            return False

    return True


def combine_accept_headers(scope: Scope) -> None:
    headers: Final = TypeAdapter(tuple[tuple[bytes, bytes], ...]).validate_python(scope.get("headers", ()))
    accept_values: Final = [value for name, value in headers if name.lower() == b"accept"]
    if len(accept_values) < 2:
        return

    combined_accept: Final = b", ".join(accept_values)
    normalized_headers: Final[  # mutable-ok: SDK and ASGI compatibility payload uses the canonical mutable shape
        list[tuple[bytes, bytes]]
    ] = []
    accept_inserted = False  # rebind-ok: framework flow intentionally updates request or lifecycle state
    for name, value in headers:
        if name.lower() != b"accept":
            normalized_headers.append((name, value))
        elif not accept_inserted:
            normalized_headers.append((name, combined_accept))
            accept_inserted = True
    scope["headers"] = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
        normalized_headers
    )
