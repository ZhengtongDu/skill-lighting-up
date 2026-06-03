# Skill Inventory

Imported on 2026-06-03.

## Reusable Personal Skills

| Skill | Source | Notes |
| --- | --- | --- |
| `humanizer` | `~/.claude/skills/humanizer` | Uses Claude copy, version `3.0.0`; nested `.git` excluded. |
| `hv-analysis` | `~/.claude/skills/hv-analysis` | Same content also existed under Codex; imported once. |
| `storage-analyzer` | `~/.claude/skills/storage-analyzer` | Same content also existed under Codex; imported once. |
| `gh-address-comments` | `~/.codex/skills/gh-address-comments` | Codex personal skill. |
| `pdf` | `~/.codex/skills/pdf` | Codex personal skill. |
| `sync-config` | repository-local | Syncs sanitized global Claude/Codex configs and skills from this repo. |

## Sanitized Global Configs

| Config | Source | Notes |
| --- | --- | --- |
| `configs/claude/settings.json` | `~/.claude/settings.json` | Removes local home-directory path-specific allow entries. |
| `configs/claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Portable rewrite; keeps `dzt` environment name, removes machine-local paths. |
| `configs/codex/AGENTS.md` | `~/.codex/AGENTS.md` | Portable rewrite; keeps `dzt` environment name, removes machine-local paths. |
| `configs/codex/rules/default.rules` | `~/.codex/rules/default.rules` | Default Codex command approval rules. |
| `configs/codex/config.toml` | `~/.codex/config.toml` | Stable template only; excludes auth, project trust, marketplace paths, notify paths, and bundled MCP paths. |

## Project Skills

| Skill | Source | Notes |
| --- | --- | --- |
| `0-autoresearch-skill` | `~/work/overleaf/.claude/skills/0-autoresearch-skill` | Overleaf/research workflow. |
| `academic-plotting` | `~/work/overleaf/.claude/skills/20-ml-paper-writing/academic-plotting` | Paper plotting workflow. |
| `ml-paper-writing` | `~/work/overleaf/.claude/skills/20-ml-paper-writing/ml-paper-writing` | ML paper writing workflow. |
| `presenting-conference-talks` | `~/work/overleaf/.claude/skills/20-ml-paper-writing/presenting-conference-talks` | Conference talk workflow. |
| `systems-paper-writing` | `~/work/overleaf/.claude/skills/20-ml-paper-writing/systems-paper-writing` | Systems paper writing workflow. |
| `brainstorming-research-ideas` | `~/work/overleaf/.claude/skills/21-research-ideation/brainstorming-research-ideas` | Research ideation workflow. |
| `creative-thinking-for-research` | `~/work/overleaf/.claude/skills/21-research-ideation/creative-thinking-for-research` | Research ideation workflow. |

## Excluded

- `~/.codex/skills/.system/*`
- `~/.codex/plugins/cache/**`
- `~/.codex/vendor_imports/**`
- `~/.claude/plugins/**`
- nested `.git` directories from installed skills
- MCP, settings, auth, history, and cache files
