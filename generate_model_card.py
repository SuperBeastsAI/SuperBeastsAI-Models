#!/usr/bin/env python3
"""
Generate MODEL_INFO.json and SHA256SUMS.txt for SuperBeasts.AI model releases.

Usage (PowerShell):
  python generate_model_card.py SuperPopColorAdjustment/v2.0/SuperBeasts_ColorAdjustment_512px_V2.safetensors \
      --model-name "Super Pop Color Adjustment" \
      --family "SuperPopColorAdjustment" \
      --version "v2.0" \
      --input-patch-px 512 \
      --license "SPCA-Community-NoSaaS" \
      --notes "Improved colour/contrast adjustments."

This will create MODEL_INFO.json and SHA256SUMS.txt in the same folder as the model file.

The script is platform-independent and works on Windows, macOS, and Linux.
"""

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import sys
from typing import Optional


def sha256_of_file(path: pathlib.Path) -> str:
    """Return SHA-256 hex digest for the given file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_license_url(repo_url: str, family: str) -> str:
    """Construct a license URL based on repo URL and family directory."""
    return f"{repo_url}/blob/main/{family}/LICENSE.txt"


def build_model_card(
    *,
    model_name: str,
    filename: str,
    family: str,
    version: str,
    input_patch_px: int,
    license_: str,
    license_url: str,
    sha256: str,
    trained_by: str,
    source_repo: str,
    notes: str,
) -> dict:
    """Return a dict ready to dump as MODEL_INFO.json."""
    today = _dt.date.today().isoformat()
    return {
        "model_name": model_name,
        "filename": filename,
        "family": family,
        "version": version,
        "input_patch_px": input_patch_px,
        "license": license_,
        "license_url": license_url,
        "sha256_preembed": sha256,  # For safetensors we use the same hash
        "trained_by": trained_by,
        "source_repo": source_repo,
        "released": today,
        "notes": notes,
        "sha256_postembed": sha256,
        "license_name": f"{model_name} ({license_})",
    }


def write_files(folder: pathlib.Path, info: dict, sha256: str, filename: str) -> None:
    """Write MODEL_INFO.json and SHA256SUMS.txt into *folder*."""
    model_info_path = folder / "MODEL_INFO.json"
    sha256sums_path = folder / "SHA256SUMS.txt"

    # Write MODEL_INFO.json (pretty-printed, deterministic order)
    with model_info_path.open("w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"✔ Wrote {model_info_path.relative_to(pathlib.Path.cwd())}")

    # Append or create SHA256SUMS.txt
    line = f"{sha256}  {filename}\n"
    if sha256sums_path.exists():
        existing = sha256sums_path.read_text(encoding="utf-8")
        if line in existing:
            print("✔ SHA256SUMS.txt already contains entry – skipping update")
            return
    with sha256sums_path.open("a", encoding="utf-8") as f:
        f.write(line)
    print(f"✔ Updated {sha256sums_path.relative_to(pathlib.Path.cwd())}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate MODEL_INFO.json & SHA256SUMS.txt for a model file.")
    p.add_argument("model_path", help="Path to the model file (e.g., SuperPopColorAdjustment/v2.0/model.safetensors)")
    p.add_argument("--model-name", required=True, help="Human-readable model name (e.g., 'Super Pop Color Adjustment')")
    p.add_argument("--family", required=True, help="Model family directory (e.g., 'SuperPopColorAdjustment')")
    p.add_argument("--version", required=True, help="Model version (e.g., 'v2.0')")
    p.add_argument("--input-patch-px", type=int, default=512, help="Input patch size in pixels (default: 512)")
    p.add_argument("--license", dest="license_", default="SPCA-Community-NoSaaS", help="License identifier")
    p.add_argument("--license-url", help="Custom license URL (defaults to repo/family/LICENSE.txt)")
    p.add_argument("--trained-by", default="SuperBeasts.AI", help="Author or organisation that trained the model")
    p.add_argument("--source-repo", default="https://github.com/SuperBeastsAI/SuperBeastsAI-Models", help="Source repository URL")
    p.add_argument("--notes", default="", help="Release notes")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)

    model_file = pathlib.Path(args.model_path).expanduser().resolve()
    if not model_file.is_file():
        sys.exit(f"Error: '{model_file}' is not a file.")

    sha256 = sha256_of_file(model_file)

    license_url = args.license_url or derive_license_url(args.source_repo, args.family)

    info = build_model_card(
        model_name=args.model_name,
        filename=model_file.name,
        family=args.family,
        version=args.version,
        input_patch_px=args.input_patch_px,
        license_=args.license_,
        license_url=license_url,
        sha256=sha256,
        trained_by=args.trained_by,
        source_repo=args.source_repo,
        notes=args.notes,
    )

    # Ensure destination folder exists (should, based on given model path)
    folder = model_file.parent
    write_files(folder, info, sha256, model_file.name)


if __name__ == "__main__":
    main() 