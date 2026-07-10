# Source Map

All values in this map are configuration names, not repository defaults. Store
real values in a local environment file that is ignored by Git, or provide them
only to the command that needs them.

## Local Workspace

- `FEISHU_REPORT_ROOT`: directory containing weekly Markdown reports.
- `FEISHU_REPORTS_DIR`: directory searched for report duplicates.
- `FEISHU_SUMMARY_FILE`: Markdown index updated after a report is complete.
- `FEISHU_SOURCE_REPO`: Git repository used to collect weekly changes.
- `FEISHU_RESEARCH_DIR`, `FEISHU_PAPER_DIR`, `FEISHU_REPORTS_RELATIVE_DIR`:
  source-repository-relative directories to index.

## Feishu Pull

- `FEISHU_APP_ID` and `FEISHU_APP_SECRET`: local API credentials.
- `FEISHU_SPACE_ID` and `FEISHU_PARENT_NODE_TOKEN`: source wiki location.
- `FEISHU_WEB_BASE_URL`: optional web URL prefix for links written to Markdown.

## Feishu Upload

- `FEISHU_UPLOAD_CLI`: local executable that uploads Markdown to Feishu.
- `FEISHU_FOLDER_TOKEN` and `FEISHU_PARENT_WIKI_URL`: upload destination.

Use `scripts/pull_feishu_weeklies.sh` and
`scripts/upload_report_to_feishu.sh` only after these values have been set.
Do not put values in this file, a committed `.env`, prompts, reports, or logs.
