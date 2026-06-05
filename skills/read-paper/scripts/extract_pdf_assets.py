#!/usr/bin/env python3
"""
从 PDF 提取图片资产，供论文解读使用。

功能：
1. 提取 PDF 中所有嵌入图片（保存为 PNG）。
2. 可选：将指定页面整页渲染为高分辨率 PNG（用于跨整页的图、表、流程图）。

依赖：PyMuPDF (fitz)。安装：
    pip3 install --user --break-system-packages PyMuPDF

用法：
    python3 extract_pdf_assets.py 论文.pdf                      # 仅提取嵌入图
    python3 extract_pdf_assets.py 论文.pdf --out /tmp/read-paper-demo/images
    python3 extract_pdf_assets.py 论文.pdf --pages 2,3,8,17       # 额外整页渲染这些页
    python3 extract_pdf_assets.py 论文.pdf --pages 2,3 --zoom 3   # 渲染缩放倍率（默认2）
"""

import argparse
import os
import re
import sys
import tempfile


def parse_args():
    p = argparse.ArgumentParser(description="从 PDF 提取嵌入图与整页渲染")
    p.add_argument("pdf", help="输入 PDF 路径")
    p.add_argument(
        "--out",
        default=None,
        help="图片输出目录（默认 /tmp/read-paper-<pdf文件名>/images）",
    )
    p.add_argument(
        "--pages",
        default="",
        help="额外整页渲染的页码（1-based，逗号分隔），如 2,3,8,17",
    )
    p.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="整页渲染缩放倍率，越大越清晰（默认 2.0）",
    )
    return p.parse_args()


def default_out_dir(pdf_path):
    stem = os.path.splitext(os.path.basename(pdf_path))[0] or "paper"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._") or "paper"
    slug = slug[:80]
    return os.path.join(tempfile.gettempdir(), f"read-paper-{slug}", "images")


def extract_embedded_images(doc, out_dir):
    """提取所有嵌入图片，返回提取数量。"""
    import fitz

    count = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            name = f"page{page_num + 1}_img{img_idx + 1}.png"
            target = os.path.join(out_dir, name)
            if pix.n < 5:  # GRAY 或 RGB
                pix.save(target)
            else:  # CMYK 等：先转 RGB
                pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                pix_rgb.save(target)
                pix_rgb = None
            pix = None
            count += 1
    return count


def render_pages(doc, out_dir, pages, zoom):
    """将指定页面（1-based）整页渲染为 PNG。"""
    import fitz

    rendered = []
    mat = fitz.Matrix(zoom, zoom)
    for p in pages:
        idx = p - 1
        if idx < 0 or idx >= len(doc):
            print(f"  [跳过] 页码 {p} 超出范围（共 {len(doc)} 页）")
            continue
        pix = doc[idx].get_pixmap(matrix=mat)
        target = os.path.join(out_dir, f"fullpage_{p}.png")
        pix.save(target)
        rendered.append(p)
    return rendered


def main():
    args = parse_args()
    out_dir = args.out or default_out_dir(args.pdf)

    try:
        import fitz  # noqa: F401
    except ImportError:
        print("缺少 PyMuPDF。请运行：pip3 install --user --break-system-packages PyMuPDF")
        sys.exit(1)

    import fitz

    if not os.path.exists(args.pdf):
        print(f"找不到 PDF：{args.pdf}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(args.pdf)

    n_imgs = extract_embedded_images(doc, out_dir)
    print(f"提取嵌入图 {n_imgs} 张 -> {out_dir}/")

    if args.pages.strip():
        try:
            pages = [int(x) for x in args.pages.split(",") if x.strip()]
        except ValueError:
            print("--pages 格式错误，应为逗号分隔的整数，如 2,3,8,17")
            doc.close()
            sys.exit(1)
        rendered = render_pages(doc, out_dir, pages, args.zoom)
        print(f"整页渲染 {len(rendered)} 页（zoom={args.zoom}）-> {out_dir}/fullpage_*.png")

    doc.close()
    print("完成。")


if __name__ == "__main__":
    main()
