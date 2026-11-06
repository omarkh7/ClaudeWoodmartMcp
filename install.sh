#!/usr/bin/env bash
# Fallback installer: copies the woodmart-builder skill into ~/.claude/skills/
# (use this if you don't install via the plugin marketplace).
# macOS / Linux. Windows: see README ("Manual install - Windows PowerShell").
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/plugins/woodmart-builder/skills/woodmart-builder"
DEST_ROOT="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
DEST="$DEST_ROOT/woodmart-builder"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "error: $SRC/SKILL.md not found - run this script from a clone of the repo." >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"

if [ -e "$DEST" ]; then
  BACKUP="$DEST.bak-$(date +%Y%m%d-%H%M%S)"
  echo "Existing install found - moving it to $BACKUP"
  mv "$DEST" "$BACKUP"
fi

cp -R "$SRC" "$DEST"
chmod +x "$DEST/scripts/"*.py 2>/dev/null || true

echo "Installed woodmart-builder skill to $DEST"
echo "Start a new Claude Code session and ask e.g. \"connect a new woodmart site\"."
