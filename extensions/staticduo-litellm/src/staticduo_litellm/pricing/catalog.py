"""Apply the versioned private catalog delta to a fresh upstream snapshot."""

from collections.abc import Mapping
from copy import deepcopy
from functools import reduce
from importlib.resources import files
from typing import Final

from pydantic import JsonValue, TypeAdapter

_JSON: Final = TypeAdapter(Mapping[str, JsonValue])
_OPERATIONS: Final = TypeAdapter(tuple[Mapping[str, JsonValue], ...])


def load_catalog_overlay() -> Mapping[str, JsonValue]:
    return _JSON.validate_json(files(__package__).joinpath("catalog-v1.json").read_text(encoding="utf-8"))


def _apply_operation(catalog: Mapping[str, JsonValue], operation: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    op: Final = operation["op"]
    model: Final = operation["model"]
    field: Final = operation.get("field")
    if op not in ("add", "replace", "remove") or not isinstance(model, str):
        raise ValueError(f"Unsupported StaticDuo catalog operation: {op}")
    if field is None:
        if op == "remove":
            return {key: value for key, value in catalog.items() if key != model}
        # A private row is authoritative, including removal of stale fields.
        return {**catalog, model: deepcopy(operation["value"])}
    if not isinstance(field, str):
        raise TypeError("StaticDuo catalog operation field must be a string")
    row: Final = catalog.get(model)
    if op == "remove":
        if not isinstance(row, dict):
            return catalog
        return {**catalog, model: {key: value for key, value in row.items() if key != field}}
    if row is not None and not isinstance(row, dict):
        raise ValueError(f"StaticDuo catalog entry must be an object: {model}")
    return {**catalog, model: {**(row or {}), field: deepcopy(operation["value"])}}


def apply_catalog_overlay(
    catalog: Mapping[str, object], overlay: Mapping[str, object] | None = None
) -> Mapping[str, JsonValue]:
    selected_overlay: Final = load_catalog_overlay() if overlay is None else overlay
    if selected_overlay.get("schema_version") != 1:
        raise ValueError("Unsupported StaticDuo catalog overlay version")
    snapshot: Final = deepcopy(_JSON.validate_python(catalog))
    operations: Final = _OPERATIONS.validate_python(selected_overlay["operations"])
    return reduce(_apply_operation, operations, snapshot)
