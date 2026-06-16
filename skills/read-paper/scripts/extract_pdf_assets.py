#!/usr/bin/env python3
"""
从 PDF 提取论文解读用的图片资产。

功能：
1. 提取 PDF 中的嵌入位图。
2. 根据 Figure/Fig. caption 自动裁剪论文图，兼容矢量图和嵌入图。
3. 可选渲染指定整页，用于表格、复杂跨栏图或低置信度回退。
4. 输出 manifest.json 和 markdown_snippets.md，方便 read-paper 写作时插图。

依赖：PyMuPDF (fitz)。安装：
    python3 -m pip install PyMuPDF

用法：
    python3 extract_pdf_assets.py paper.pdf
    python3 extract_pdf_assets.py paper.pdf --out /tmp/read-paper-demo/images
    python3 extract_pdf_assets.py paper.pdf --pages 2,3,8 --zoom 3
    python3 extract_pdf_assets.py paper.pdf --markdown-prefix attachments/read-paper-demo
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CAPTION_RE = re.compile(
    r"^\s*(?P<label>(?:Figure|Fig\.?)\s*(?P<number>\d+[A-Za-z]?(?:\.\d+)?))"
    r"\s*[:.\-]?\s*(?P<caption>.*)",
    re.IGNORECASE,
)

METHOD_TERMS = {
    "architecture",
    "pipeline",
    "framework",
    "overview",
    "model",
    "method",
    "algorithm",
    "system",
    "workflow",
    "training",
    "inference",
    "transformer",
    "network",
    "attention",
    "adaptation",
    "reparametrization",
    "rank",
    "low",
    "train",
}

EXPERIMENT_TERMS = {
    "result",
    "accuracy",
    "performance",
    "comparison",
    "ablation",
    "benchmark",
    "evaluation",
    "validation",
    "scalability",
}

EXAMPLE_TERMS = {
    "example",
    "qualitative",
    "case",
    "failure",
    "visualization",
    "prediction",
    "input",
    "output",
    "sample",
    "examples",
}

BACKGROUND_TERMS = {
    "dataset",
    "task",
    "problem",
    "distribution",
    "statistics",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 PDF 提取论文图片资产和 Figure 裁剪图")
    parser.add_argument("pdf", help="输入 PDF 路径")
    parser.add_argument(
        "--out",
        default=None,
        help="输出目录（默认 /tmp/read-paper-<pdf文件名>/images）",
    )
    parser.add_argument(
        "--pages",
        default="",
        help="额外整页渲染的页码（1-based，逗号分隔），如 2,3,8,17",
    )
    parser.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="整页渲染缩放倍率，越大越清晰（默认 2.0）",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=260,
        help="Figure 裁剪图渲染 DPI（默认 260）",
    )
    parser.add_argument(
        "--markdown-prefix",
        default="",
        help="markdown_snippets.md 中图片路径前缀，如 attachments/read-paper-demo",
    )
    parser.add_argument(
        "--no-embedded",
        action="store_true",
        help="不提取 PDF 嵌入位图",
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="不按 Figure caption 自动裁剪论文图",
    )
    return parser.parse_args()


def import_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        print("缺少 PyMuPDF。请运行：python3 -m pip install PyMuPDF", file=sys.stderr)
        raise SystemExit(1) from exc
    return fitz


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str, limit: int = 80) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (slug or "paper")[:limit]


def default_out_dir(pdf_path: str) -> str:
    stem = os.path.splitext(os.path.basename(pdf_path))[0] or "paper"
    return os.path.join(tempfile.gettempdir(), f"read-paper-{slugify(stem)}", "images")


def parse_page_list(value: str) -> list[int]:
    pages: list[int] = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        if "-" in item:
            left, right = item.split("-", 1)
            if left.strip().isdigit() and right.strip().isdigit():
                start = int(left)
                end = int(right)
                pages.extend(range(min(start, end), max(start, end) + 1))
            continue
        if item.isdigit():
            pages.append(int(item))
    seen: set[int] = set()
    output: list[int] = []
    for page in pages:
        if page > 0 and page not in seen:
            seen.add(page)
            output.append(page)
    return output


def rel_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def markdown_path(relative_path: str, prefix: str) -> str:
    clean_prefix = prefix.strip().strip("/")
    if not clean_prefix:
        return relative_path
    return f"{clean_prefix}/{relative_path}"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def short_text(value: str, limit: int = 180) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def clip_rect(fitz: Any, rect: Any, page_rect: Any) -> Any:
    clipped = fitz.Rect(
        max(page_rect.x0, rect.x0),
        max(page_rect.y0, rect.y0),
        min(page_rect.x1, rect.x1),
        min(page_rect.y1, rect.y1),
    )
    return clipped


def expand_rect(fitz: Any, rect: Any, page_rect: Any, x_margin: float = 8.0, y_margin: float = 8.0) -> Any:
    expanded = fitz.Rect(
        rect.x0 - x_margin,
        rect.y0 - y_margin,
        rect.x1 + x_margin,
        rect.y1 + y_margin,
    )
    return clip_rect(fitz, expanded, page_rect)


def union_rects(fitz: Any, rects: Iterable[Any]) -> Any | None:
    iterator = iter(rects)
    try:
        rect = fitz.Rect(next(iterator))
    except StopIteration:
        return None
    for item in iterator:
        rect |= fitz.Rect(item)
    return rect


def rect_area(rect: Any) -> float:
    return max(rect.width, 0.0) * max(rect.height, 0.0)


def horizontal_overlap(a: Any, b: Any) -> float:
    return max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))


def vertical_overlap(a: Any, b: Any) -> float:
    return max(0.0, min(a.y1, b.y1) - max(a.y0, b.y0))


def rect_distance(a: Any, b: Any) -> float:
    dx = max(b.x0 - a.x1, a.x0 - b.x1, 0.0)
    dy = max(b.y0 - a.y1, a.y0 - b.y1, 0.0)
    return (dx * dx + dy * dy) ** 0.5


def extract_block_text(block: dict[str, Any]) -> str:
    parts: list[str] = []
    for line in block.get("lines", []):
        if not isinstance(line, dict):
            continue
        for span in line.get("spans", []):
            if not isinstance(span, dict):
                continue
            text = span.get("text")
            if isinstance(text, str):
                parts.append(text)
    return clean_text("".join(parts))


def text_blocks_for_page(fitz: Any, page: Any) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    page_dict = page.get_text("dict", sort=True)
    for block in page_dict.get("blocks", []):
        if not isinstance(block, dict) or block.get("type") != 0:
            continue
        text = extract_block_text(block)
        if not text:
            continue
        blocks.append({"rect": fitz.Rect(block["bbox"]), "text": text})
    return blocks


def image_blocks_for_page(fitz: Any, page: Any) -> list[Any]:
    rects: list[Any] = []
    page_dict = page.get_text("dict", sort=True)
    for block in page_dict.get("blocks", []):
        if not isinstance(block, dict) or block.get("type") != 1:
            continue
        rect = clip_rect(fitz, fitz.Rect(block["bbox"]), page.rect)
        if rect.width >= 2 and rect.height >= 2:
            rects.append(rect)
    return rects


def drawing_rects_for_page(fitz: Any, page: Any) -> list[Any]:
    rects: list[Any] = []
    page_area = max(rect_area(page.rect), 1.0)
    for drawing in page.get_drawings():
        raw_rect = drawing.get("rect")
        if raw_rect is None:
            continue
        rect = clip_rect(fitz, fitz.Rect(raw_rect), page.rect)
        area = rect_area(rect)
        if rect.width < 1.5 or rect.height < 1.5:
            continue
        if area < 8:
            continue
        if area / page_area > 0.18:
            continue
        if rect.width > page.rect.width * 0.92 and rect.height < 5:
            continue
        rects.append(rect)
    return rects


def caption_records(fitz: Any, doc: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[int, str, int]] = set()
    for page_index in range(len(doc)):
        page = doc[page_index]
        for block_index, block in enumerate(text_blocks_for_page(fitz, page)):
            match = CAPTION_RE.match(block["text"])
            if not match:
                continue
            label = clean_text(match.group("label")).replace("Fig.", "Figure")
            number = match.group("number")
            caption = block["text"]
            key = (page_index, number, round(block["rect"].y0))
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "page_index": page_index,
                    "page_number": page_index + 1,
                    "block_index": block_index,
                    "label": label,
                    "number": number,
                    "caption": caption,
                    "caption_rect": block["rect"],
                }
            )
    return records


def select_visual_rect(fitz: Any, page: Any, caption_rect: Any, direction: str) -> tuple[Any | None, str]:
    page_rect = page.rect
    page_height = page_rect.height
    page_width = page_rect.width
    visual_rects = image_blocks_for_page(fitz, page) + drawing_rects_for_page(fitz, page)
    if not visual_rects:
        return None, "no-visual-objects"

    caption_window = fitz.Rect(
        max(page_rect.x0, caption_rect.x0 - page_width * 0.30),
        page_rect.y0,
        min(page_rect.x1, caption_rect.x1 + page_width * 0.30),
        page_rect.y1,
    )
    candidates: list[Any] = []
    for rect in visual_rects:
        if direction == "above":
            gap = caption_rect.y0 - rect.y1
            in_band = -12 <= gap <= page_height * 0.58
            not_crossing_caption = rect.y0 < caption_rect.y0 - 2
        else:
            gap = rect.y0 - caption_rect.y1
            in_band = -12 <= gap <= page_height * 0.58
            not_crossing_caption = rect.y1 > caption_rect.y1 + 2
        near_x = horizontal_overlap(rect, caption_window) > 0
        center_near = abs(((rect.x0 + rect.x1) / 2) - ((caption_rect.x0 + caption_rect.x1) / 2)) <= page_width * 0.42
        if in_band and not_crossing_caption and (near_x or center_near):
            candidates.append(rect)

    if not candidates:
        return None, "no-nearby-visual-objects"

    seed = [
        rect
        for rect in candidates
        if horizontal_overlap(rect, caption_window) > 0
        or abs(((rect.x0 + rect.x1) / 2) - ((caption_rect.x0 + caption_rect.x1) / 2)) <= page_width * 0.25
    ]
    if not seed:
        seed = candidates

    cluster = list(seed)
    current = union_rects(fitz, cluster)
    if current is None:
        return None, "empty-cluster"

    changed = True
    while changed:
        changed = False
        expanded = expand_rect(fitz, current, page_rect, x_margin=36, y_margin=28)
        for rect in candidates:
            if rect in cluster:
                continue
            if horizontal_overlap(rect, expanded) > 0 and vertical_overlap(rect, expanded) > 0:
                cluster.append(rect)
                current |= rect
                changed = True
            elif rect_distance(rect, current) <= 34:
                cluster.append(rect)
                current |= rect
                changed = True

    return current, "visual-objects"


def include_annotation_text(fitz: Any, page: Any, visual_rect: Any, caption_rect: Any, direction: str) -> Any:
    page_rect = page.rect
    expanded_visual = expand_rect(fitz, visual_rect, page_rect, x_margin=16, y_margin=16)
    rects = [visual_rect]
    for block in text_blocks_for_page(fitz, page):
        rect = block["rect"]
        text = block["text"]
        if rect == caption_rect:
            continue
        if CAPTION_RE.match(text):
            continue
        if len(text) > 140 and rect_area(rect) > page_rect.width * 20:
            continue
        if direction == "above" and rect.y0 >= caption_rect.y0 - 1:
            continue
        if direction == "below" and rect.y1 <= caption_rect.y1 + 1:
            continue
        center = fitz.Point((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2)
        center_inside = expanded_visual.contains(center)
        overlap_area = horizontal_overlap(rect, expanded_visual) * vertical_overlap(rect, expanded_visual)
        if center_inside or overlap_area >= min(rect_area(rect), rect_area(expanded_visual)) * 0.20:
            rects.append(rect)
    merged = union_rects(fitz, rects)
    return merged if merged is not None else visual_rect


def fallback_caption_clip(fitz: Any, page: Any, caption_rect: Any, direction: str) -> Any:
    page_rect = page.rect
    if direction == "below":
        top = min(page_rect.y1, caption_rect.y1 + 4)
        bottom = min(page_rect.y1, top + page_rect.height * 0.42)
    else:
        bottom = max(page_rect.y0, caption_rect.y0 - 4)
        top = max(page_rect.y0, bottom - page_rect.height * 0.42)
    return fitz.Rect(page_rect.x0 + 6, top, page_rect.x1 - 6, bottom)


def crop_for_caption(fitz: Any, doc: Any, record: dict[str, Any]) -> tuple[Any, str, str]:
    page = doc[record["page_index"]]
    caption_rect = record["caption_rect"]
    page_rect = page.rect

    above_rect, above_reason = select_visual_rect(fitz, page, caption_rect, "above")
    below_rect, below_reason = select_visual_rect(fitz, page, caption_rect, "below")

    direction = "above"
    visual_rect = above_rect
    reason = above_reason
    if below_rect is not None:
        if visual_rect is None or rect_area(below_rect) > rect_area(visual_rect) * 1.15:
            direction = "below"
            visual_rect = below_rect
            reason = below_reason

    if visual_rect is None:
        fallback = fallback_caption_clip(fitz, page, caption_rect, direction)
        return expand_rect(fitz, fallback, page_rect, x_margin=2, y_margin=2), "low", reason

    with_text = include_annotation_text(fitz, page, visual_rect, caption_rect, direction)
    crop = expand_rect(fitz, with_text, page_rect, x_margin=8, y_margin=8)
    if direction == "above":
        crop.y1 = min(crop.y1, caption_rect.y0 - 2)
    else:
        crop.y0 = max(crop.y0, caption_rect.y1 + 2)
    crop = clip_rect(fitz, crop, page_rect)
    confidence = "high" if rect_area(crop) > page_rect.width * page_rect.height * 0.015 else "medium"
    return crop, confidence, reason


def classify_placement(caption: str) -> str:
    lowered = caption.lower()
    tokens = set(re.findall(r"[a-z0-9]+", lowered))
    if tokens & EXAMPLE_TERMS:
        return "examples"
    if tokens & EXPERIMENT_TERMS:
        return "experiments"
    if tokens & METHOD_TERMS:
        return "method"
    if tokens & BACKGROUND_TERMS:
        return "background"
    return "near-related-section"


def render_clip(page: Any, rect: Any, target: Path, dpi: int) -> None:
    pixmap = page.get_pixmap(clip=rect, dpi=dpi, alpha=False)
    pixmap.save(target.as_posix())


def extract_figure_crops(fitz: Any, doc: Any, out_dir: Path, markdown_prefix_value: str, dpi: int) -> list[dict[str, Any]]:
    figure_dir = out_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    figures: list[dict[str, Any]] = []
    used_names: set[str] = set()

    for index, record in enumerate(caption_records(fitz, doc), start=1):
        page = doc[record["page_index"]]
        crop, confidence, reason = crop_for_caption(fitz, doc, record)
        number_slug = slugify(record["number"].replace(".", "-"), limit=24)
        base_name = f"figure-{number_slug}-p{record['page_number']:03d}"
        file_name = f"{base_name}.png"
        if file_name in used_names:
            file_name = f"{base_name}-{index}.png"
        used_names.add(file_name)
        target = figure_dir / file_name
        render_clip(page, crop, target, dpi=dpi)
        relative = rel_path(target, out_dir)
        md_path = markdown_path(relative, markdown_prefix_value)
        caption = record["caption"]
        label = record["label"]
        snippet = f"![{short_text(caption, 120)}]({md_path})\n\n*{caption}*"
        figures.append(
            {
                "index": index,
                "label": label,
                "number": record["number"],
                "page": record["page_number"],
                "caption": caption,
                "placement_hint": classify_placement(caption),
                "confidence": confidence,
                "crop_reason": reason,
                "bbox": [round(crop.x0, 3), round(crop.y0, 3), round(crop.x1, 3), round(crop.y1, 3)],
                "path": target.resolve().as_posix(),
                "relative_path": relative,
                "markdown_path": md_path,
                "markdown": snippet,
            }
        )
    return figures


def extract_embedded_images(fitz: Any, doc: Any, out_dir: Path) -> list[dict[str, Any]]:
    embedded_dir = out_dir / "embedded"
    embedded_dir.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, Any]] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_idx, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            name = f"page{page_num + 1:03d}-img{img_idx:02d}.png"
            target = embedded_dir / name
            if pix.n < 5:
                pix.save(target.as_posix())
            else:
                pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                pix_rgb.save(target.as_posix())
                pix_rgb = None
            pix = None
            assets.append(
                {
                    "page": page_num + 1,
                    "image_index": img_idx,
                    "path": target.resolve().as_posix(),
                    "relative_path": rel_path(target, out_dir),
                }
            )
    return assets


def render_pages(fitz: Any, doc: Any, out_dir: Path, pages: list[int], zoom: float) -> list[dict[str, Any]]:
    fullpage_dir = out_dir / "fullpages"
    fullpage_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, Any]] = []
    mat = fitz.Matrix(zoom, zoom)
    for page in pages:
        idx = page - 1
        if idx < 0 or idx >= len(doc):
            print(f"  [跳过] 页码 {page} 超出范围（共 {len(doc)} 页）")
            continue
        target = fullpage_dir / f"fullpage-p{page:03d}.png"
        pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
        pix.save(target.as_posix())
        rendered.append(
            {
                "page": page,
                "path": target.resolve().as_posix(),
                "relative_path": rel_path(target, out_dir),
            }
        )
    return rendered


def write_markdown_snippets(out_dir: Path, figures: list[dict[str, Any]]) -> Path:
    target = out_dir / "markdown_snippets.md"
    lines = ["# Extracted Paper Figures", ""]
    if not figures:
        lines.extend(["未检测到 Figure caption。", ""])
    for figure in figures:
        lines.extend(
            [
                f"## {figure['label']}，page {figure['page']}，{figure['placement_hint']}，confidence={figure['confidence']}",
                "",
                figure["markdown"],
                "",
            ]
        )
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"找不到 PDF：{pdf_path}", file=sys.stderr)
        return 1

    fitz = import_fitz()
    out_dir = Path(args.out or default_out_dir(args.pdf))
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path.as_posix())
    page_count = len(doc)
    try:
        embedded = [] if args.no_embedded else extract_embedded_images(fitz, doc, out_dir)
        figures = [] if args.no_figures else extract_figure_crops(fitz, doc, out_dir, args.markdown_prefix, args.dpi)
        rendered = render_pages(fitz, doc, out_dir, parse_page_list(args.pages), args.zoom) if args.pages.strip() else []
    finally:
        doc.close()

    snippets_path = write_markdown_snippets(out_dir, figures)
    manifest = {
        "generated_at": now_utc_iso(),
        "pdf_path": pdf_path.resolve().as_posix(),
        "output_dir": out_dir.resolve().as_posix(),
        "page_count": page_count,
        "figures": figures,
        "embedded_images": embedded,
        "fullpage_renders": rendered,
        "markdown_snippets": snippets_path.resolve().as_posix(),
        "notes": [
            "figures 是按 Figure/Fig. caption 裁剪的论文图，优先用于 Markdown 插图。",
            "embedded_images 是 PDF 内部位图，常包含碎片或低语义小图，必要时再人工筛选。",
            "confidence=low 时应打开图片或整页渲染复核；复杂表格建议用 --pages 渲染整页。",
        ],
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Figure 裁剪 {len(figures)} 张 -> {out_dir / 'figures'}")
    print(f"嵌入图提取 {len(embedded)} 张 -> {out_dir / 'embedded'}")
    if rendered:
        print(f"整页渲染 {len(rendered)} 页 -> {out_dir / 'fullpages'}")
    print(f"manifest -> {manifest_path}")
    print(f"markdown snippets -> {snippets_path}")
    print("完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
