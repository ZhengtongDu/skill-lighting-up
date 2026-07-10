---
name: feishu-weekly-report
description: Generate a concise weekly research report from configured local Git
  sources, optionally publish it to Feishu, and update the local report index.
  Use when the user asks to prepare this week's Feishu weekly report or a weekly
  research-and-paper-reading summary.
---

# Feishu Weekly Report

This skill is portable: the workspace, source repository, Feishu destinations,
and upload command are local configuration, never values embedded in this
repository. Read `references/source-map.md` and configure only the variables
needed for the requested operation.

## Configuration

Resolve locations in this order: an explicit path in the user's request or
command, then the documented environment variable. If a required value is
missing, ask for it rather than guessing a home directory, organization, or
Feishu destination.

- Report workspace: `FEISHU_REPORT_ROOT`.
- Source Git repository: `FEISHU_SOURCE_REPO`.
- Source subdirectories: `FEISHU_RESEARCH_DIR`, `FEISHU_PAPER_DIR`, and
  `FEISHU_REPORTS_RELATIVE_DIR`.
- Local report index: `FEISHU_SUMMARY_FILE`.
- Feishu API and upload settings are needed only for pull/upload operations.

Never print, commit, or summarize environment files, app IDs, app secrets,
access tokens, destination tokens, private Feishu URLs, or shell startup
secrets.

## Workflow

1. Compute the week with `scripts/compute_week.py`. Weeks are Monday-Sunday in
   `Asia/Shanghai`; report IDs use `YYMMDD-YYMMDD`.
2. Resolve the report file under the configured report workspace. Read the
   previous report only if it exists, then summarize its `下周计划` as
   `上周计划完成情况`.
3. If local sources are configured, run `scripts/index_git_sources.py` with
   the computed week boundaries. Include uncommitted changes only when the user
   has asked for a current-state report.
4. Use `scripts/find_report_duplicates.py` to avoid repeating papers. Prefer
   title matching and use source paths only as a secondary signal.
5. Draft the Markdown report using `references/report-format.md`. Keep it
   concise enough for a group update and distinguish new progress from context.
6. Update the local index with `scripts/update_summary.py`.
7. Run `scripts/pull_feishu_weeklies.sh` only when the user asks to import
   remote reports. Run `scripts/upload_report_to_feishu.sh` only when the user
   asks to publish the completed report. Both require local configuration.
8. Commit or push the report repository only when the user explicitly asks.

## Report Content

Required sections:

- `一、本周科研内容`
- `二、本周阅读论文`
- `三、下周计划`

For research progress, summarize the week's completed work, evidence or
decisions, blockers, and a concrete next-week plan. For papers, start with a
rough/deep reading count; each paper should include its source note, selected
visual evidence where available, an abstract-level summary, and a clearly
labelled personal analysis.

Use visual inspection to choose paper figures. Prefer a title/abstract image,
then an optional method or result image. Do not select images only from file
names.

## Model Handoff Contract

A model can complete the local draft when given the report root and source
repository. It must state which configuration it used, list any missing values,
and stop before Feishu publication if the user did not explicitly request it.
This makes the skill usable on a new machine without copying another person's
paths or credentials.
