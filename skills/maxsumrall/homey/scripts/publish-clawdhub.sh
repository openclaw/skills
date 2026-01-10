#!/usr/bin/env bash
set -euo pipefail

# Publishes this skill folder to ClawdHub using the official `clawdhub` CLI.
#
# Requirements (CI):
# - `clawdhub` must be installed and on PATH
# - CLAWDHUB_API_KEY must be set (GitHub secret)
#
# Optional env overrides:
# - CLAWDHUB_SLUG
# - CLAWDHUB_NAME
# - CLAWDHUB_TAGS (default: latest)
# - CLAWDHUB_CHANGELOG (default: empty)

if [ -z "${CLAWDHUB_API_KEY:-}" ]; then
  echo "error: CLAWDHUB_API_KEY is not set" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v clawdhub >/dev/null 2>&1; then
  echo "error: clawdhub CLI not found on PATH (install with: npm i -g clawdhub)" >&2
  exit 2
fi

PACKAGE_VERSION="$(node -p "require('${ROOT_DIR}/package.json').version")"

# Prefer the git tag version (v1.2.3) in CI; fallback to package.json.
VERSION=""
if [ -n "${GITHUB_REF_NAME:-}" ] && [[ "${GITHUB_REF_NAME}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
  VERSION="${GITHUB_REF_NAME#v}"
  if [ "$VERSION" != "$PACKAGE_VERSION" ]; then
    echo "error: tag version ($VERSION) does not match package.json version ($PACKAGE_VERSION)" >&2
    exit 2
  fi
else
  VERSION="$PACKAGE_VERSION"
fi

# Extract default slug from SKILL.md frontmatter (name: ...)
DEFAULT_SLUG="$(node -e "const fs=require('fs'); const s=fs.readFileSync('SKILL.md','utf8'); const m=s.match(/^name:\s*([^\n]+)$/m); process.stdout.write(m?m[1].trim():'');")"

SLUG="${CLAWDHUB_SLUG:-${DEFAULT_SLUG:-}}"
NAME="${CLAWDHUB_NAME:-Homey}"
TAGS="${CLAWDHUB_TAGS:-latest}"
CHANGELOG="${CLAWDHUB_CHANGELOG:-}"

if [ -z "$SLUG" ]; then
  echo "error: could not determine slug. Set CLAWDHUB_SLUG or add 'name:' to SKILL.md frontmatter." >&2
  exit 2
fi

echo "clawdhub publish: slug=${SLUG} version=${VERSION} tags=${TAGS}" >&2

# Non-interactive login using token.
clawdhub --no-input login --token "$CLAWDHUB_API_KEY" --no-browser >/dev/null

# Publish the skill folder (repo root contains SKILL.md)
clawdhub --no-input publish "$ROOT_DIR" \
  --slug "$SLUG" \
  --name "$NAME" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags "$TAGS" >/dev/null

echo "ok: published ${SLUG}@${VERSION} (${TAGS})" >&2
