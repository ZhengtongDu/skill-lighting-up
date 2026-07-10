#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path


def run_git(repo: Path, args: list[str]) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", *args], text=True, capture_output=True)
    if proc.returncode != 0:
        return ""
    return proc.stdout


def run_git_bytes(repo: Path, args: list[str]) -> bytes:
    proc = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", *args], capture_output=True)
    if proc.returncode != 0:
        return b""
    return proc.stdout


def parse_status_z(data: bytes) -> list[str]:
    paths: list[str] = []
    parts = [p.decode("utf-8", errors="replace") for p in data.split(b"\0") if p]
    i = 0
    while i < len(parts):
        entry = parts[i]
        if len(entry) < 4:
            i += 1
            continue
        status = entry[:2]
        path = entry[3:]
        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            if i + 1 < len(parts):
                paths.append(parts[i + 1])
                i += 2
                continue
        paths.append(path)
        i += 1
    return paths


def paper_kind(path: str) -> str | None:
    name = Path(path).name
    if "(deep-done)" in name:
        return "deep"
    if "(done)" in name:
        return "rough"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("FEISHU_SOURCE_REPO"))
    parser.add_argument("--research-dir", default=os.environ.get("FEISHU_RESEARCH_DIR", "research"))
    parser.add_argument("--paper-dir", default=os.environ.get("FEISHU_PAPER_DIR", "papers"))
    parser.add_argument("--reports-dir", default=os.environ.get("FEISHU_REPORTS_RELATIVE_DIR", "reports"))
    parser.add_argument("--week-start", required=True)
    parser.add_argument("--week-end-plus-1", required=True)
    args = parser.parse_args()

    if not args.repo:
        parser.error("--repo or FEISHU_SOURCE_REPO is required")

    repo = Path(args.repo)
    tracked_dirs = [args.research_dir, args.paper_dir, args.reports_dir]
    since = f"{args.week_start} 00:00:00"
    until = f"{args.week_end_plus_1} 00:00:00"

    status = run_git(repo, ["status", "--short", "--", *tracked_dirs])
    status_z = run_git_bytes(repo, ["status", "--porcelain=v1", "-z", "--", *tracked_dirs])
    changed_status_paths = parse_status_z(status_z)

    log_names = run_git(
        repo,
        [
            "log",
            "--since",
            since,
            "--until",
            until,
            "--name-only",
            "--pretty=format:",
            "--",
            args.research_dir,
            args.paper_dir,
        ],
    )
    changed_log_paths = [p.strip() for p in log_names.splitlines() if p.strip()]

    all_paths = sorted(set(changed_status_paths + changed_log_paths))
    research_prefix = f"{args.research_dir.rstrip('/')}/"
    paper_prefix = f"{args.paper_dir.rstrip('/')}/"
    research = [p for p in all_paths if p.startswith(research_prefix)]
    paper_paths = [p for p in all_paths if p.startswith(paper_prefix) and p.endswith(".md")]

    all_done = []
    readpaper = repo / args.paper_dir
    if readpaper.exists():
        for path in sorted(readpaper.glob("*.md")):
            rel = path.relative_to(repo).as_posix()
            kind = paper_kind(rel)
            if kind:
                all_done.append({"path": rel, "kind": kind, "title": path.stem})

    changed_papers = []
    for rel in paper_paths:
        kind = paper_kind(rel)
        if kind:
            changed_papers.append({"path": rel, "kind": kind, "title": Path(rel).stem})

    result = {
        "repo": str(repo),
        "research_dir": args.research_dir,
        "paper_dir": args.paper_dir,
        "week_start": args.week_start,
        "week_end_plus_1": args.week_end_plus_1,
        "status": status,
        "changed_paths": all_paths,
        "research_candidates": research,
        "changed_paper_candidates": changed_papers,
        "all_done_papers": all_done,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
