#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: upload_report_to_feishu.sh --file /path/to/week.md [--title 260615-260621]
USAGE
}

require_env() {
  local name=$1
  if [[ -z "${!name:-}" ]]; then
    echo "missing required environment variable: $name" >&2
    exit 2
  fi
}

file=""
title=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      file="$2"; shift 2 ;;
    --title)
      title="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$file" ]]; then
  usage
  exit 1
fi
if [[ ! -f "$file" ]]; then
  echo "file not found: $file" >&2
  exit 1
fi
if [[ -n "${FEISHU_ENV_FILE:-}" ]]; then
  if [[ ! -f "$FEISHU_ENV_FILE" ]]; then
    echo "FEISHU_ENV_FILE does not exist: $FEISHU_ENV_FILE" >&2
    exit 2
  fi
  # shellcheck disable=SC1090
  source "$FEISHU_ENV_FILE"
fi
require_env FEISHU_UPLOAD_CLI
require_env FEISHU_FOLDER_TOKEN
require_env FEISHU_PARENT_WIKI_URL

if [[ ! -x "$FEISHU_UPLOAD_CLI" ]]; then
  echo "FEISHU_UPLOAD_CLI is not executable: $FEISHU_UPLOAD_CLI" >&2
  exit 2
fi
if [[ -z "$title" ]]; then
  base="$(basename "$file")"
  title="${base%.*}"
fi

"$FEISHU_UPLOAD_CLI" \
  --no-proxy \
  --file "$file" \
  --folder-token "$FEISHU_FOLDER_TOKEN" \
  --title "$title" \
  --parent-wiki-url "$FEISHU_PARENT_WIKI_URL"
