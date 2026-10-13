"""Generate release catalogs without changing the tracked upstream sources."""

import argparse
import hashlib
import json
from pathlib import Path

from staticduo_litellm.pricing.catalog import apply_catalog_overlay, load_catalog_overlay


def generate_catalog(source: Path, output_dir: Path) -> dict[str, object]:
    raw = source.read_bytes()
    overlay = load_catalog_overlay()
    overlay_bytes = json.dumps(overlay, sort_keys=True, separators=(",", ":")).encode()
    generated = (json.dumps(apply_catalog_overlay(json.loads(raw)), indent=4) + "\n").encode()
    manifest = {
        "schema_version": 1,
        "overlay_version": overlay["overlay_version"],
        "overlay_sha256": hashlib.sha256(overlay_bytes).hexdigest(),
        "overlay_upstream_commit": overlay["upstream_commit"],
        "overlay_effective_baseline_commit": overlay["effective_baseline_commit"],
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "generated_sha256": hashlib.sha256(generated).hexdigest(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("model_prices_and_context_window.json", "model_prices_and_context_window_backup.json"):
        (output_dir / name).write_bytes(generated)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    generate_catalog(args.source, args.output_dir)


if __name__ == "__main__":
    main()
