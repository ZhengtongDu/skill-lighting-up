#!/usr/bin/env python3
"""Merge stable Codex config template into an existing config.toml.

The template owns only stable global preferences. Machine-local sections are
preserved from the existing destination file.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MANAGED_TOP_LEVEL_KEYS = {
    "model",
    "model_reasoning_effort",
}

MANAGED_SECTIONS = {
    '[plugins."documents@openai-primary-runtime"]',
    '[plugins."spreadsheets@openai-primary-runtime"]',
    '[plugins."presentations@openai-primary-runtime"]',
    '[plugins."browser@openai-bundled"]',
    "[desktop]",
    "[desktop.open-in-target-preferences]",
    "[features]",
}


def section_header(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        return stripped
    return None


def top_level_key(line: str, in_section: bool) -> str | None:
    if in_section:
        return None
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip()


def filter_existing(text: str) -> str:
    lines: list[str] = []
    skip_section = False
    in_section = False

    for line in text.splitlines():
        header = section_header(line)
        if header is not None:
            in_section = True
            skip_section = header in MANAGED_SECTIONS
            if skip_section:
                continue

        if skip_section:
            continue

        key = top_level_key(line, in_section)
        if key in MANAGED_TOP_LEVEL_KEYS:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--dest", required=True, type=Path)
    args = parser.parse_args()

    template = args.template.read_text()
    existing = args.dest.read_text() if args.dest.exists() else ""
    preserved = filter_existing(existing)

    merged = template.strip() + "\n"
    if preserved:
        merged += "\n# Machine-local and unmanaged settings preserved below.\n"
        merged += preserved + "\n"

    args.dest.parent.mkdir(parents=True, exist_ok=True)
    args.dest.write_text(merged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
