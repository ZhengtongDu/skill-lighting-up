---
name: sync-config
description: |
  Synchronize Claude Code and Codex global permission/config files and personal
  skills from a configured skill-lighting-up repository.
  Use when the user asks to sync, install, update, or standardize Claude Code
  or Codex configuration/skills on a new local machine or server.
---

# Sync Config

Use this skill to synchronize Claude Code and Codex global configuration and
skills from the `skill-lighting-up` repository.

## Scope

The repository stores one portable, sanitized source of truth:

- `configs/unified-agent-config.json`

The sync script renders target-specific files from that unified config:

- Claude Code global `settings.json`
- Claude Code global `CLAUDE.md`
- Codex global `AGENTS.md`
- Codex global `rules/default.rules`
- stable Codex `config.toml` preferences
- personal reusable skills

It does not store auth, tokens, `.env`, MCP runtime paths, marketplace cache
paths, chat history, project trust state, or machine-local secrets.

## Procedure

Clone the repository URL supplied by the user (or the current checkout's
`origin` URL) into `/tmp`, then run the sync script for the calling agent. If
no repository URL is available, ask rather than guessing an account or fork.

When this skill is running inside Codex, use:

```sh
tmpdir=$(mktemp -d /tmp/skill-lighting-up.XXXXXX)
git clone "<repository-url>" "$tmpdir/skill-lighting-up"
cd "$tmpdir/skill-lighting-up"
./scripts/sync_config.sh --agent codex
```

When this skill is running inside Claude Code, use:

```sh
tmpdir=$(mktemp -d /tmp/skill-lighting-up.XXXXXX)
git clone "<repository-url>" "$tmpdir/skill-lighting-up"
cd "$tmpdir/skill-lighting-up"
./scripts/sync_config.sh --agent claude
```

If the user explicitly asks to configure both tools:

```sh
./scripts/sync_config.sh --agent both
```

`--agent auto` is available, but explicit `codex` or `claude` is preferred
because the running shell environment may not always expose a reliable marker.

For Codex only:

```sh
./scripts/sync_config.sh --agent codex
```

For Claude Code only:

```sh
./scripts/sync_config.sh --agent claude
```

To update only skills:

```sh
./scripts/sync_config.sh --skills-only --agent codex
```

To update only global configs:

```sh
./scripts/sync_config.sh --configs-only --agent codex
```

Project skills are skipped by default. Include them only when the target machine
should have research/paper-writing project skills installed globally:

```sh
./scripts/sync_config.sh --include-project-skills
```

## After Sync

Restart Claude Code and Codex sessions so both tools reload their global
configuration and skill list.
