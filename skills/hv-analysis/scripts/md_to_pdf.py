#!/usr/bin/env python3
"""
横纵分析法报告 Markdown -> PDF 转换脚本。

这是轻量包装器：PDF 转换委托给 BetterMarkdownHelper/markdown-publisher
的 Pandoc + XeLaTeX 实现。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_markdown_publisher_root() -> Path:
    """定位 BetterMarkdownHelper/markdown-publisher 根目录。"""
    env = os.environ.get("MARKDOWN_PUBLISHER_ROOT") or os.environ.get("BETTER_MARKDOWN_HELPER_ROOT")
    candidates = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend(
        [
            Path.home() / "work" / "BetterMarkdownHelper" / "markdown-publisher",
            Path.home() / "BetterMarkdownHelper" / "markdown-publisher",
        ]
    )

    for root in candidates:
        cli = root / "packages" / "cli" / "dist" / "index.js"
        exporters = root / "packages" / "cli" / "dist" / "exporters.js"
        template = root / "templates" / "latex" / "default-cn.tex"
        if cli.exists() and exporters.exists() and template.exists():
            return root

    checked = "\n".join(f"  - {p}" for p in candidates)
    raise FileNotFoundError(
        "未找到 BetterMarkdownHelper/markdown-publisher。请设置 MARKDOWN_PUBLISHER_ROOT。\n"
        f"已检查:\n{checked}"
    )


def build_template(root: Path, work_dir: Path) -> Path:
    """复制 BetterMarkdownHelper 模板，并按本机可用字体集调整 ctex fontset。"""
    source = root / "templates" / "latex" / "default-cn.tex"
    fontset = os.environ.get("MARKDOWN_PUBLISHER_FONTSET", "fandol")
    text = source.read_text(encoding="utf-8")
    text = text.replace("fontset=mac", f"fontset={fontset}")
    target = work_dir / "default-cn.tex"
    target.write_text(text, encoding="utf-8")
    return target


def run_markdown_publisher(input_path: Path, output_path: Path, pdf_engine: str) -> None:
    root = find_markdown_publisher_root()
    exporters = root / "packages" / "cli" / "dist" / "exporters.js"
    with tempfile.TemporaryDirectory(prefix="hv-mdpub-") as tmp:
        template = build_template(root, Path(tmp))
        run_export_pdf(root, exporters, template, input_path, output_path, pdf_engine)


def run_export_pdf(
    root: Path,
    exporters: Path,
    template: Path,
    input_path: Path,
    output_path: Path,
    pdf_engine: str,
) -> None:
    js = f"""
import fs from "node:fs/promises";
import path from "node:path";
import {{ exportPdf }} from {json.dumps(exporters.as_uri())};

const inputAbs = {json.dumps(str(input_path))};
const requestedOutput = {json.dumps(str(output_path))};
const outputDir = path.dirname(requestedOutput);

const result = await exportPdf(
  {{ inputAbs, baseDir: {json.dumps(str(root))} }},
  {{
    engine: {json.dumps(pdf_engine)},
    template: {json.dumps(str(template))},
    outputDir,
    pandocArgs: [],
  }},
);

if (path.resolve(result.outputPath) !== path.resolve(requestedOutput)) {{
  await fs.copyFile(result.outputPath, requestedOutput);
}}

for (const warning of result.warnings) {{
  console.warn(`WARN: ${{warning}}`);
}}
console.log(`OK: ${{requestedOutput}}`);
"""

    node = shutil.which("node")
    if not node:
        raise RuntimeError("未找到 node。BetterMarkdownHelper/markdown-publisher 需要 Node.js >= 18。")

    completed = subprocess.run(
        [node, "--input-type=module", "--eval", js],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.stderr:
        print(completed.stderr.strip(), file=sys.stderr)
    if completed.returncode != 0:
        raise RuntimeError(f"markdown-publisher 导出失败(code {completed.returncode})")


def main() -> None:
    parser = argparse.ArgumentParser(description="横纵分析报告 Markdown -> PDF")
    parser.add_argument("input", help="输入 Markdown 文件")
    parser.add_argument("output", help="输出 PDF 文件")
    parser.add_argument("--pdf-engine", default="xelatex", help="Pandoc PDF 引擎，默认 xelatex")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    if output_path.suffix.lower() != ".pdf":
        raise ValueError("输出文件必须是 .pdf")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_markdown_publisher(input_path, output_path, args.pdf_engine)

    size_kb = output_path.stat().st_size / 1024
    print(f"[OK] PDF 已生成: {output_path} ({size_kb:.1f} KB, engine=markdown-publisher/{args.pdf_engine})")


if __name__ == "__main__":
    main()
