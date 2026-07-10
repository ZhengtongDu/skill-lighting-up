#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", default=os.environ.get("FEISHU_REPORTS_DIR"))
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--source-path", action="append", default=[])
    parser.add_argument("--exclude-week", default="")
    args = parser.parse_args()

    if not args.reports_dir:
        parser.error("--reports-dir or FEISHU_REPORTS_DIR is required")

    reports_dir = Path(args.reports_dir)
    results = []
    for report in sorted(reports_dir.glob("*.md")):
        if args.exclude_week and report.stem == args.exclude_week:
            continue
        text = report.read_text(encoding="utf-8", errors="replace")
        hits = []
        lower = text.lower()
        for title in args.title:
            if title and title.lower() in lower:
                hits.append({"type": "title", "value": title})
        for source in args.source_path:
            if source and source in text:
                hits.append({"type": "source_path", "value": source})
        if hits:
            results.append({"report": str(report), "week_id": report.stem, "hits": hits})

    print(json.dumps({"duplicates": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
