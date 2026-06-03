# skill-lighting-up

Reusable personal skills for Claude Code and Codex.

This repository is intended to be the source of truth for skills that should
travel across local machines and servers.

## Layout

```text
skills/
  gh-address-comments/
  humanizer/
  hv-analysis/
  pdf/
  storage-analyzer/

project-skills/
  overleaf/
    0-autoresearch-skill/
    academic-plotting/
    brainstorming-research-ideas/
    creative-thinking-for-research/
    ml-paper-writing/
    presenting-conference-talks/
    systems-paper-writing/
```

## Install

Install reusable personal skills to both Claude Code and Codex:

```sh
./install.sh
```

Install only for Claude Code:

```sh
./install.sh --target claude
```

Install only for Codex:

```sh
./install.sh --target codex
```

Also install `project-skills/` globally:

```sh
./install.sh --include-project-skills
```

By default, project skills are not installed globally. Copy them into a
project-local `.claude/skills/` directory when they are specific to one
repository or workflow.

## What Is Not Stored Here

Do not commit:

- API keys, tokens, auth files, or `.env` files
- MCP server configuration
- Claude Code or Codex settings
- chat history, cache, logs, or project state
- plugin cache directories or vendor-imported system skills

## Update From This Machine

```sh
git switch -c import-current-skills
# update skills/
git add .
git commit -m "Import current personal and reusable skills"
git push origin import-current-skills
```

Open a PR and review the diff before merging.
