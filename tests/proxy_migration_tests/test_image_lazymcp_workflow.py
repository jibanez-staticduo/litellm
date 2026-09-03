from __future__ import annotations

from pathlib import Path
from typing import Final, cast

import yaml
from yaml import BaseLoader

WORKFLOW: Final = Path(__file__).parents[2] / ".github/workflows/image-scan.yml"
PROTECTED_RUNTIME_PATHS: Final = frozenset(
    {
        "gateway/routes/allowlist.py",
        "litellm/proxy/proxy_server.py",
        "litellm/proxy/_lazy_features.py",
        "litellm/proxy/_lazy_openapi_snapshot.py",
        "litellm/proxy/_lazy_openapi_snapshot.json",
        "litellm/proxy/lazymcp_routes.py",
        "litellm/proxy/_experimental/mcp_server/**",
    }
)


def test_image_scan_triggers_for_every_lazymcp_runtime_owner() -> None:
    loaded: Final[object] = yaml.load(WORKFLOW.read_text(), Loader=BaseLoader)  # pyright: ignore[reportAny]  # PyYAML stubs return Any
    assert isinstance(loaded, dict)
    workflow: Final = cast(dict[object, object], loaded)
    trigger: Final = workflow.get("on") or workflow.get(True)
    assert isinstance(trigger, dict)
    trigger_mapping: Final = cast(dict[object, object], trigger)
    pull_request: Final = trigger_mapping.get("pull_request")
    assert isinstance(pull_request, dict)
    pull_request_mapping: Final = cast(dict[object, object], pull_request)
    paths: Final = pull_request_mapping.get("paths")
    assert isinstance(paths, list)
    path_values: Final = cast(list[object], paths)
    assert all(isinstance(path, str) for path in path_values)
    assert PROTECTED_RUNTIME_PATHS <= set(cast(list[str], path_values))
