import copy
import json
import subprocess
from pathlib import Path

from staticduo_litellm.pricing.catalog import apply_catalog_overlay, load_catalog_overlay

ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = "541e3ed5305a530ebef74d5684d3aca2632c1009"
BASELINE = "f5eaab5396f957c5529456bbb545e52ce0b48c46"


def snapshot(revision, name="model_prices_and_context_window.json"):
    return json.loads(subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=ROOT))


def test_overlay_reproduces_effective_baseline_and_preserves_input():
    overlay = load_catalog_overlay()
    assert overlay["upstream_commit"] == UPSTREAM
    for name in ("model_prices_and_context_window.json", "litellm/model_prices_and_context_window_backup.json"):
        source = snapshot(UPSTREAM, name)
        pristine = copy.deepcopy(source)
        assert apply_catalog_overlay(source) == snapshot(BASELINE, name)
        assert source == pristine
        assert json.loads((ROOT / name).read_text()) == pristine


def test_fresh_generation_removes_fields_and_is_idempotent():
    first = apply_catalog_overlay(snapshot(UPSTREAM))
    assert apply_catalog_overlay(first) == first
    refreshed = snapshot(UPSTREAM)
    refreshed["gpt-image-2.5-flare"]["input_cost_per_token"] = 123
    refreshed["gpt-image-2.5-flare"]["supports_pdf_input"] = True
    refreshed["chatgpt/gpt-live-1-codex"] = {"stale": True}
    result = apply_catalog_overlay(refreshed)
    assert result["gpt-image-2.5-flare"]["input_cost_per_token"] == 123
    assert "supports_pdf_input" not in result["gpt-image-2.5-flare"]
    assert "stale" not in result["chatgpt/gpt-live-1-codex"]
    assert apply_catalog_overlay(result) == result


def test_explicit_row_deletion_and_fresh_reload():
    overlay = {
        "schema_version": 1,
        "operations": [
            {"op": "remove", "model": "obsolete"},
            {"op": "remove", "model": "current", "field": "stale"},
            {"op": "replace", "model": "current", "field": "price", "value": 2},
            {"op": "add", "model": "private", "value": {"price": 3}},
        ],
    }
    result = apply_catalog_overlay({"obsolete": {}, "current": {"price": 1, "stale": True}}, overlay)
    assert result == {"current": {"price": 2}, "private": {"price": 3}}
    assert apply_catalog_overlay(result, overlay) == result
    assert apply_catalog_overlay({"current": {"price": 7, "fresh": 1}}, overlay)["current"] == {"price": 2, "fresh": 1}


def test_build_generator_has_deterministic_provenance_and_preserves_source(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("catalog_generator", ROOT / "scripts/generate_staticduo_catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = ROOT / "model_prices_and_context_window.json"
    raw = source.read_bytes()
    manifest = module.generate_catalog(source, tmp_path)
    first = (tmp_path / "model_prices_and_context_window.json").read_bytes()
    assert json.loads(first) == snapshot(BASELINE)
    assert module.generate_catalog(source, tmp_path) == manifest
    assert (tmp_path / "model_prices_and_context_window_backup.json").read_bytes() == first
    assert source.read_bytes() == raw
    assert manifest["overlay_version"] == "1.0.0"
    assert len(manifest["overlay_sha256"]) == 64


def test_core_refresh_applies_overlay_before_alias_expansion_without_mutation():
    from litellm.litellm_core_utils.get_model_cost_map import _finalize_model_cost_map

    source = snapshot(UPSTREAM)
    source["fresh-model"] = {"input_cost_per_token": 1, "aliases": ["fresh-alias"]}
    pristine = copy.deepcopy(source)
    first = _finalize_model_cost_map(source)
    assert source == pristine
    assert "supports_pdf_input" not in first["gpt-image-2.5-flare"]
    assert first["fresh-alias"] == first["fresh-model"]
    source["fresh-model"]["input_cost_per_token"] = 2
    second = _finalize_model_cost_map(source)
    assert second["fresh-alias"]["input_cost_per_token"] == 2
    assert first["fresh-alias"]["input_cost_per_token"] == 1
