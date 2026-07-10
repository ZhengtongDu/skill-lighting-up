#!/usr/bin/env bash
set -euo pipefail

require_env() {
  local name=$1
  if [[ -z "${!name:-}" ]]; then
    echo "missing required environment variable: $name" >&2
    exit 2
  fi
}

if [[ -n "${FEISHU_ENV_FILE:-}" ]]; then
  if [[ ! -f "$FEISHU_ENV_FILE" ]]; then
    echo "FEISHU_ENV_FILE does not exist: $FEISHU_ENV_FILE" >&2
    exit 2
  fi
  # shellcheck disable=SC1090
  source "$FEISHU_ENV_FILE"
fi

require_env FEISHU_REPORT_ROOT
require_env FEISHU_APP_ID
require_env FEISHU_APP_SECRET
require_env FEISHU_SPACE_ID
require_env FEISHU_PARENT_NODE_TOKEN

WORKSPACE_DIR=$FEISHU_REPORT_ROOT
OUT_DIR="${FEISHU_REPORTS_DIR:-$WORKSPACE_DIR/$(date '+%Y')}"
OVERWRITE="${OVERWRITE:-0}"
API_BASE="${FEISHU_API_BASE:-https://open.feishu.cn/open-apis}"
WEB_BASE="${FEISHU_WEB_BASE_URL:-https://feishu.cn}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "missing command: $1" >&2; exit 1; }
}

json_escape() {
  jq -Rn --arg v "$1" '$v'
}

safe_filename() {
  printf '%s' "$1" | tr '/:' '--' | tr -cd '[:alnum:]_. -'
}

need_cmd curl
need_cmd jq
mkdir -p "$OUT_DIR"

APP_ID_JSON="$(json_escape "$FEISHU_APP_ID")"
APP_SECRET_JSON="$(json_escape "$FEISHU_APP_SECRET")"
TOKEN_RESP="$(
  curl --noproxy '*' -sS -X POST "$API_BASE/auth/v3/tenant_access_token/internal" \
    -H 'Content-Type: application/json; charset=utf-8' \
    -d "{\"app_id\":$APP_ID_JSON,\"app_secret\":$APP_SECRET_JSON}"
)"
TOKEN="$(printf '%s' "$TOKEN_RESP" | jq -r '.tenant_access_token // empty')"

if [[ -z "$TOKEN" ]]; then
  printf '%s\n' "$TOKEN_RESP" | jq '{code,msg}' >&2
  exit 1
fi

page_token=""
total=0
written=0
skipped=0

while :; do
  url="$API_BASE/wiki/v2/spaces/$FEISHU_SPACE_ID/nodes?parent_node_token=$FEISHU_PARENT_NODE_TOKEN&page_size=50"
  if [[ -n "$page_token" ]]; then
    url="$url&page_token=$page_token"
  fi

  LIST_RESP="$(curl --noproxy '*' -sS -X GET "$url" -H "Authorization: Bearer $TOKEN")"
  code="$(printf '%s' "$LIST_RESP" | jq -r '.code')"
  if [[ "$code" != "0" ]]; then
    printf '%s\n' "$LIST_RESP" | jq '{code,msg}' >&2
    exit 1
  fi

  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    title="$(printf '%s' "$item" | jq -r '.title')"
    obj_token="$(printf '%s' "$item" | jq -r '.obj_token')"
    obj_type="$(printf '%s' "$item" | jq -r '.obj_type')"
    node_token="$(printf '%s' "$item" | jq -r '.node_token')"
    out_file="$OUT_DIR/$(safe_filename "$title").md"
    total=$((total + 1))

    if [[ -f "$out_file" && "$OVERWRITE" != "1" ]]; then
      echo "[skip] $out_file"
      skipped=$((skipped + 1))
      continue
    fi
    if [[ "$obj_type" != "docx" ]]; then
      echo "[skip] $title: unsupported obj_type=$obj_type" >&2
      skipped=$((skipped + 1))
      continue
    fi

    CONTENT_RESP="$(
      curl --noproxy '*' -sS -X GET "$API_BASE/docx/v1/documents/$obj_token/raw_content" \
        -H "Authorization: Bearer $TOKEN"
    )"
    content_code="$(printf '%s' "$CONTENT_RESP" | jq -r '.code')"
    if [[ "$content_code" != "0" ]]; then
      printf '%s\n' "$CONTENT_RESP" | jq '{code,msg}' >&2
      exit 1
    fi

    content="$(printf '%s' "$CONTENT_RESP" | jq -r '.data.content // ""')"
    tmp_file="$out_file.tmp"
    {
      printf '%s\n' '---'
      printf 'title: "%s"\n' "$title"
      printf 'source: "feishu"\n'
      printf 'feishu_url: "%s/docx/%s"\n' "${WEB_BASE%/}" "$obj_token"
      printf 'feishu_node_token: "%s"\n' "$node_token"
      printf 'feishu_docx_token: "%s"\n' "$obj_token"
      printf 'pulled_at: "%s"\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
      printf '%s\n\n' '---'
      printf '# %s\n\n' "$title"
      printf '%s\n' "$content" | sed '1d'
    } > "$tmp_file"
    mv "$tmp_file" "$out_file"
    echo "[write] $out_file"
    written=$((written + 1))
  done < <(printf '%s' "$LIST_RESP" | jq -c '.data.items | sort_by(.title)[]')

  has_more="$(printf '%s' "$LIST_RESP" | jq -r '.data.has_more')"
  [[ "$has_more" == "true" ]] || break
  page_token="$(printf '%s' "$LIST_RESP" | jq -r '.data.page_token')"
done

echo "done: total=$total written=$written skipped=$skipped out_dir=$OUT_DIR"
