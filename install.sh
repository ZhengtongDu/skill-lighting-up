#!/bin/sh
set -eu

TARGET="both"
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
    --include-project-skills)
      INCLUDE_PROJECT_SKILLS=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./install.sh [--target both|claude|codex] [--include-project-skills]

Installs skills/ into:
  ~/.claude/skills
  ~/.codex/skills

Project skills are skipped unless --include-project-skills is passed.
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

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

copy_skill_dir() {
  src_root=$1
  dest_root=$2

  [ -d "$src_root" ] || return 0
  mkdir -p "$dest_root"

  for skill_dir in "$src_root"/*; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    dest="$dest_root/$skill_name"
    rm -rf "$dest"
    mkdir -p "$dest"
    tar -C "$skill_dir" -cf - . | tar -C "$dest" -xf -
    printf 'Installed %s -> %s\n' "$skill_name" "$dest"
  done
}

install_target() {
  dest_root=$1
  copy_skill_dir "$ROOT/skills" "$dest_root"

  if [ "$INCLUDE_PROJECT_SKILLS" -eq 1 ]; then
    find "$ROOT/project-skills" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | while IFS= read -r skill_dir; do
      skill_name=$(basename "$skill_dir")
      dest="$dest_root/$skill_name"
      rm -rf "$dest"
      mkdir -p "$dest"
      tar -C "$skill_dir" -cf - . | tar -C "$dest" -xf -
      printf 'Installed project skill %s -> %s\n' "$skill_name" "$dest"
    done
  fi
}

if [ "$TARGET" = "both" ] || [ "$TARGET" = "claude" ]; then
  install_target "$HOME/.claude/skills"
fi

if [ "$TARGET" = "both" ] || [ "$TARGET" = "codex" ]; then
  install_target "$HOME/.codex/skills"
fi
