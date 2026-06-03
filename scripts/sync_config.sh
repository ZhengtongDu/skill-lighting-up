#!/bin/sh
set -eu

AGENT="auto"
MODE="all"
INCLUDE_PROJECT_SKILLS=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --agent|--target)
      AGENT="${2:-}"
      shift 2
      ;;
    --agent=*|--target=*)
      AGENT="${1#*=}"
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
Usage: scripts/sync_config.sh [--agent auto|codex|claude|both] [--skills-only|--configs-only] [--include-project-skills]

Synchronizes from one source file:
  configs/unified-agent-config.json

Agent behavior:
  --agent codex   install Codex global config and Codex skills
  --agent claude  install Claude Code global config and Claude skills
  --agent both    install both
  --agent auto    infer from the calling agent when possible

Machine-local auth, project trust, marketplace cache paths, notifications, and
MCP runtime paths are not stored in this repository.
EOF
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

case "$AGENT" in
  auto|both|claude|codex) ;;
  *)
    printf 'Invalid --agent: %s\n' "$AGENT" >&2
    exit 2
    ;;
esac

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNIFIED_CONFIG="$ROOT/configs/unified-agent-config.json"
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="$HOME/.config-backups/skill-lighting-up-sync-$TS"

detect_agent() {
  if [ "${SYNC_CONFIG_AGENT:-}" = "codex" ] || [ "${SYNC_CONFIG_AGENT:-}" = "claude" ] || [ "${SYNC_CONFIG_AGENT:-}" = "both" ]; then
    printf '%s\n' "$SYNC_CONFIG_AGENT"
    return
  fi

  if [ -n "${CODEX_HOME:-}" ] || [ -n "${CODEX_CLI_PATH:-}" ] || [ -n "${CODEX_SANDBOX:-}" ]; then
    printf 'codex\n'
    return
  fi

  if [ -n "${CLAUDE_CONFIG_DIR:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ] || [ -n "${CLAUDECODE:-}" ]; then
    printf 'claude\n'
    return
  fi

  printf 'unknown\n'
}

if [ "$AGENT" = "auto" ]; then
  AGENT=$(detect_agent)
  if [ "$AGENT" = "unknown" ]; then
    cat >&2 <<'EOF'
Could not infer whether this request came from Codex or Claude Code.
Run again with one of:
  scripts/sync_config.sh --agent codex
  scripts/sync_config.sh --agent claude
  scripts/sync_config.sh --agent both
EOF
    exit 2
  fi
fi

backup_file() {
  src=$1
  name=$2
  if [ -f "$src" ]; then
    mkdir -p "$BACKUP"
    cp "$src" "$BACKUP/$name"
  fi
}

render_configs() {
  out_dir=$1
  mkdir -p "$out_dir"

  if [ "$AGENT" = "codex" ] || [ "$AGENT" = "both" ]; then
    python3 "$ROOT/scripts/render_agent_config.py" \
      --config "$UNIFIED_CONFIG" \
      --agent "$AGENT" \
      --output-dir "$out_dir" \
      --merge-codex-dest "$HOME/.codex/config.toml"
  else
    python3 "$ROOT/scripts/render_agent_config.py" \
      --config "$UNIFIED_CONFIG" \
      --agent "$AGENT" \
      --output-dir "$out_dir"
  fi
}

sync_claude_configs() {
  rendered=$1
  mkdir -p "$HOME/.claude"
  backup_file "$HOME/.claude/settings.json" "claude-settings.json"
  backup_file "$HOME/.claude/CLAUDE.md" "CLAUDE.md"
  cp "$rendered/claude/settings.json" "$HOME/.claude/settings.json"
  cp "$rendered/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
}

sync_codex_configs() {
  rendered=$1
  mkdir -p "$HOME/.codex/rules"
  backup_file "$HOME/.codex/config.toml" "codex-config.toml"
  backup_file "$HOME/.codex/AGENTS.md" "AGENTS.md"
  backup_file "$HOME/.codex/rules/default.rules" "codex-default.rules"
  cp "$rendered/codex/config.toml" "$HOME/.codex/config.toml"
  cp "$rendered/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
  cp "$rendered/codex/rules/default.rules" "$HOME/.codex/rules/default.rules"
}

sync_skills() {
  args="--target $AGENT"
  if [ "$INCLUDE_PROJECT_SKILLS" -eq 1 ]; then
    args="$args --include-project-skills"
  fi
  # shellcheck disable=SC2086
  "$ROOT/install.sh" $args
}

if [ "$MODE" = "all" ] || [ "$MODE" = "configs" ]; then
  rendered_dir=$(mktemp -d /tmp/skill-lighting-up-rendered.XXXXXX)
  render_configs "$rendered_dir"

  if [ "$AGENT" = "both" ] || [ "$AGENT" = "claude" ]; then
    sync_claude_configs "$rendered_dir"
  fi
  if [ "$AGENT" = "both" ] || [ "$AGENT" = "codex" ]; then
    sync_codex_configs "$rendered_dir"
  fi
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "skills" ]; then
  sync_skills
fi

printf 'Sync complete for agent: %s\n' "$AGENT"
if [ -d "$BACKUP" ]; then
  printf 'Backup: %s\n' "$BACKUP"
fi
