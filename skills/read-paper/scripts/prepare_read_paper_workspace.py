#!/usr/bin/env python3
"""Create and report the workspace paths for one read-paper task."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


DEFAULT_READPAPER_DIR = Path.home() / "Documents" / "ReadPaper"


def slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^read-paper-", "", value, flags=re.IGNORECASE)
    value = value.replace("_", "-")
    value = re.sub(r"[^A-Za-z0-9.+-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value.lower() or "paper"


def safe_note_name(value: str) -> str:
    value = value.strip().replace("/", "-").replace(":", "-")
    value = re.sub(r"\s+", " ", value)
    return value or "paper"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create ReadPaper note, attachment, and temporary directories."
    )
    parser.add_argument("--slug", help="Stable paper slug, for example nacs or 2108.10821.")
    parser.add_argument("--title", help="Paper title or recognizable note name.")
    parser.add_argument("--source", help="Optional PDF path or URL used as a slug fallback.")
    parser.add_argument("--filename", help="Override the Markdown filename.")
    parser.add_argument(
        "--readpaper-dir",
        help=(
            "Override ReadPaper root. Defaults to READ_PAPER_DIR, then "
            "OBSIDIAN_VAULT_DIR/ReadPaper, then ~/Documents/ReadPaper."
        ),
    )
    return parser.parse_args()


def resolve_readpaper_dir(value: str | None) -> Path:
    """Resolve a portable output root without embedding a user's vault path."""
    if value:
        return Path(value).expanduser()

    configured_dir = os.environ.get("READ_PAPER_DIR")
    if configured_dir:
        return Path(configured_dir).expanduser()

    vault_dir = os.environ.get("OBSIDIAN_VAULT_DIR")
    if vault_dir:
        return Path(vault_dir).expanduser() / "ReadPaper"

    return DEFAULT_READPAPER_DIR


def infer_slug(args: argparse.Namespace) -> str:
    if args.slug:
        return slugify(args.slug)
    if args.title:
        return slugify(args.title)
    if args.source:
        source = args.source.rstrip("/")
        stem = Path(source).stem if "://" not in source else source.rsplit("/", 1)[-1]
        return slugify(stem)
    return "paper"


def main() -> None:
    args = parse_args()
    slug = infer_slug(args)
    attachment_dir_name = f"read-paper-{slug}"

    readpaper_dir = resolve_readpaper_dir(args.readpaper_dir)
    temp_dir = Path(tempfile.gettempdir()) / f"read-paper-{slug}"
    attachments_dir = readpaper_dir / "attachments" / attachment_dir_name

    note_stem = safe_note_name(args.filename) if args.filename else f"论文解读_{slug}.md"
    markdown_name = note_stem if note_stem.endswith(".md") else f"{note_stem}.md"
    markdown_file = readpaper_dir / markdown_name

    for directory in (readpaper_dir, readpaper_dir / "attachments", attachments_dir, temp_dir):
        directory.mkdir(parents=True, exist_ok=True)

    payload = {
        "slug": slug,
        "readpaper_dir": str(readpaper_dir),
        "markdown_file": str(markdown_file),
        "markdown_exists": markdown_file.exists(),
        "attachments_dir": str(attachments_dir),
        "attachment_prefix": f"attachments/{attachment_dir_name}",
        "temp_dir": str(temp_dir),
        "pdf_file": str(temp_dir / "paper.pdf"),
        "text_file": str(temp_dir / "paper.txt"),
        "images_dir": str(temp_dir / "images"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
