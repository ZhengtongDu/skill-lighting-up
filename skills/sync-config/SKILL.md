---
name: sync-config
description: |
  Synchronize this user's Claude Code and Codex global permission/config files
  and personal skills from git@github.com:ZhengtongDu/skill-lighting-up.git.
  Use when the user asks to sync, install, update, or standardize Claude Code
  or Codex configuration/skills on a new local machine or server.
---

# Sync Config

Use this skill to synchronize Claude Code and Codex global configuration and
skills from the `skill-lighting-up` repository.

## Scope

The repository stores only portable, sanitized configuration:

- Claude Code global `settings.json`
- Claude Code global `CLAUDE.md`
- Codex global `AGENTS.md`
- Codex global `rules/default.rules`
- stable Codex `config.toml` preferences
- personal reusable skills

It does not store auth, tokens, `.env`, MCP runtime paths, marketplace cache
paths, chat history, project trust state, or machine-local secrets.

## Procedure

Clone into `/tmp` and run the sync script:

```sh
tmpdir=$(mktemp -d /tmp/skill-lighting-up.XXXXXX)
git clone git@github.com:ZhengtongDu/skill-lighting-up.git "$tmpdir/skill-lighting-up"
cd "$tmpdir/skill-lighting-up"
./scripts/sync_config.sh --target both
```

For Codex only:

```sh
./scripts/sync_config.sh --target codex
```

For Claude Code only:

```sh
./scripts/sync_config.sh --target claude
```

To update only skills:

```sh
./scripts/sync_config.sh --skills-only --target both
```

To update only global configs:

```sh
./scripts/sync_config.sh --configs-only --target both
```

Project skills are skipped by default. Include them only when the target machine
should have research/paper-writing project skills installed globally:

```sh
./scripts/sync_config.sh --include-project-skills
```

## After Sync

Restart Claude Code and Codex sessions so both tools reload their global
configuration and skill list.
