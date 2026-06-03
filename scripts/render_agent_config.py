#!/usr/bin/env python3
"""Render Claude Code and Codex config files from one unified JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return str(value)
    raise TypeError(f"Unsupported TOML value: {value!r}")


def render_codex_toml(config: dict[str, Any]) -> str:
    codex = config["codex"]["config"]
    lines: list[str] = [
        "# Generated from configs/unified-agent-config.json.",
        "# Machine-local auth, project trust, marketplace paths, notifications,",
        "# and bundled MCP runtime paths are intentionally not stored here.",
        "",
    ]

    for key, value in codex.get("top_level", {}).items():
        lines.append(f"{key} = {toml_value(value)}")

    for section in codex.get("sections", []):
        lines.append("")
        lines.append(f"[{section['name']}]")
        for key, value in section.get("values", {}).items():
            lines.append(f"{key} = {toml_value(value)}")

    return "\n".join(lines).rstrip() + "\n"


def managed_codex_sections(config: dict[str, Any]) -> set[str]:
    return {f"[{s['name']}]" for s in config["codex"]["config"].get("sections", [])}


def managed_codex_top_level_keys(config: dict[str, Any]) -> set[str]:
    return set(config["codex"]["config"].get("top_level", {}).keys())


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


def filter_existing_codex_config(text: str, config: dict[str, Any]) -> str:
    managed_sections = managed_codex_sections(config)
    managed_keys = managed_codex_top_level_keys(config)
    lines: list[str] = []
    skip_section = False
    in_section = False

    for line in text.splitlines():
        header = section_header(line)
        if header is not None:
            in_section = True
            skip_section = header in managed_sections
            if skip_section:
                continue

        if skip_section:
            continue

        key = top_level_key(line, in_section)
        if key in managed_keys:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def merge_codex_config(template: str, existing: str, config: dict[str, Any]) -> str:
    if not config["codex"]["config"].get("preserve_unmanaged_existing_config", True):
        return template

    preserved = filter_existing_codex_config(existing, config)
    merged = template.rstrip() + "\n"
    if preserved:
        merged += "\n# Machine-local and unmanaged settings preserved below.\n"
        merged += preserved + "\n"
    return merged


def render_claude(config: dict[str, Any], output_dir: Path) -> None:
    settings = dict(config["claude"].get("settings", {}))
    settings["permissions"] = config["claude"]["permissions"]

    claude_dir = output_dir / "claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    (claude_dir / "settings.json").write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n"
    )
    (claude_dir / "CLAUDE.md").write_text(config["common"]["personal_defaults_markdown"])


def render_codex(config: dict[str, Any], output_dir: Path, merge_dest: Path | None) -> None:
    codex_dir = output_dir / "codex"
    rules_dir = codex_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    template = render_codex_toml(config)
    if merge_dest is not None:
        existing = merge_dest.read_text() if merge_dest.exists() else ""
        rendered_config = merge_codex_config(template, existing, config)
    else:
        rendered_config = template

    (codex_dir / "config.toml").write_text(rendered_config)
    (codex_dir / "AGENTS.md").write_text(config["common"]["personal_defaults_markdown"])
    (rules_dir / "default.rules").write_text("\n".join(config["codex"]["rules"]).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--agent", choices=["claude", "codex", "both"], required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--merge-codex-dest", type=Path)
    args = parser.parse_args()

    config = json.loads(args.config.read_text())

    if args.agent in {"claude", "both"}:
        render_claude(config, args.output_dir)

    if args.agent in {"codex", "both"}:
        render_codex(config, args.output_dir, args.merge_codex_dest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
