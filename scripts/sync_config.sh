#!/bin/sh
set -eu

TARGET="both"
MODE="all"
INCLUDE_PROJECT_SKILLS=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --target=*)
      TARGET="${1#*=}"
      shift
      ;;
    --skills-only)
      MODE="skills"
      shift
      ;;
    --configs-only)
      MODE="configs"
      shift
      ;;
    --include-project-skills)
      INCLUDE_PROJECT_SKILLS=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: scripts/sync_config.sh [--target both|claude|codex] [--skills-only|--configs-only] [--include-project-skills]

Synchronizes:
  - Claude Code global config: ~/.claude/settings.json, ~/.claude/CLAUDE.md
  - Codex global config: ~/.codex/config.toml, ~/.codex/AGENTS.md, ~/.codex/rules/default.rules
  - skills/ into ~/.claude/skills and/or ~/.codex/skills

Machine-local auth, project trust, marketplace cache paths, and MCP runtime paths
are not stored in this repository.
EOF
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

case "$TARGET" in
  both|claude|codex) ;;
  *)
    printf 'Invalid --target: %s\n' "$TARGET" >&2
    exit 2
    ;;
esac

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="$HOME/.config-backups/skill-lighting-up-sync-$TS"

backup_file() {
  src=$1
  name=$2
  if [ -f "$src" ]; then
    mkdir -p "$BACKUP"
    cp "$src" "$BACKUP/$name"
  fi
}

sync_claude_configs() {
  mkdir -p "$HOME/.claude"
  backup_file "$HOME/.claude/settings.json" "claude-settings.json"
  backup_file "$HOME/.claude/CLAUDE.md" "CLAUDE.md"
  cp "$ROOT/configs/claude/settings.json" "$HOME/.claude/settings.json"
  cp "$ROOT/configs/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
}

sync_codex_configs() {
  mkdir -p "$HOME/.codex/rules"
  backup_file "$HOME/.codex/config.toml" "codex-config.toml"
  backup_file "$HOME/.codex/AGENTS.md" "AGENTS.md"
  backup_file "$HOME/.codex/rules/default.rules" "codex-default.rules"
  python3 "$ROOT/scripts/merge_codex_config.py" \
    --template "$ROOT/configs/codex/config.toml" \
    --dest "$HOME/.codex/config.toml"
  cp "$ROOT/configs/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  cp "$ROOT/configs/codex/rules/default.rules" "$HOME/.codex/rules/default.rules"
}

sync_skills() {
  args="--target $TARGET"
  if [ "$INCLUDE_PROJECT_SKILLS" -eq 1 ]; then
    args="$args --include-project-skills"
  fi
  # shellcheck disable=SC2086
  "$ROOT/install.sh" $args
}

if [ "$MODE" = "all" ] || [ "$MODE" = "configs" ]; then
  if [ "$TARGET" = "both" ] || [ "$TARGET" = "claude" ]; then
    sync_claude_configs
  fi
  if [ "$TARGET" = "both" ] || [ "$TARGET" = "codex" ]; then
    sync_codex_configs
  fi
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "skills" ]; then
  sync_skills
fi

printf 'Sync complete.\n'
if [ -d "$BACKUP" ]; then
  printf 'Backup: %s\n' "$BACKUP"
fi
