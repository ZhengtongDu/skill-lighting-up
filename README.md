# skill-lighting-up

Reusable personal skills for Claude Code and Codex.

This repository is intended to be the source of truth for skills that should
travel across local machines and servers. It also stores sanitized, portable
global Claude Code and Codex configuration templates.

## Layout

```text
skills/
  gh-address-comments/
  humanizer/
  hv-analysis/
  pdf/
  sync-config/
  storage-analyzer/

configs/
  claude/
    CLAUDE.md
    settings.json
  codex/
    AGENTS.md
    config.toml
    rules/default.rules

scripts/
  merge_codex_config.py
  sync_config.sh

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

## Sync Global Configs And Skills

On another machine or server, clone the repo into `/tmp` and run:

```sh
tmpdir=$(mktemp -d /tmp/skill-lighting-up.XXXXXX)
git clone git@github.com:ZhengtongDu/skill-lighting-up.git "$tmpdir/skill-lighting-up"
cd "$tmpdir/skill-lighting-up"
./scripts/sync_config.sh --target both
```

This synchronizes:

- Claude Code `~/.claude/settings.json`
- Claude Code `~/.claude/CLAUDE.md`
- Codex `~/.codex/AGENTS.md`
- Codex `~/.codex/rules/default.rules`
- stable Codex `~/.codex/config.toml` preferences
- reusable skills in `skills/`

The Codex config merge preserves machine-local sections such as auth,
project trust, marketplace cache paths, notification paths, and bundled MCP
runtime paths.

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
