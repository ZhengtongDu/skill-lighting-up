#!/usr/bin/env python3
import argparse
import os
from pathlib import Path


HEADER = """# 周报 Summary

> 本文件简要记录每周周报主题和进展。后续由 `feishu-weekly-report` skill 每周更新。

| 周报 | 主题 | 科研进展摘要 | 论文阅读 | 飞书状态 |
|---|---|---|---|---|
"""


def cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default=os.environ.get("FEISHU_SUMMARY_FILE"))
    parser.add_argument("--week-id", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--research", required=True)
    parser.add_argument("--papers", required=True)
    parser.add_argument("--status", default="已上传")
    args = parser.parse_args()

    if not args.summary:
        parser.error("--summary or FEISHU_SUMMARY_FILE is required")

    path = Path(args.summary)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else HEADER.splitlines()
    row = f"| {cell(args.week_id)} | {cell(args.topic)} | {cell(args.research)} | {cell(args.papers)} | {cell(args.status)} |"

    replaced = False
    out = []
    for line in lines:
        if line.startswith(f"| {args.week_id} |"):
            out.append(row)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if not out or not any(line.startswith("|---") for line in out):
            out = HEADER.rstrip("\n").splitlines()
        out.append(row)

    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
