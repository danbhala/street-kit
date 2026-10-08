#!/usr/bin/env bash
# Install or upgrade Street Kit (shared art for Dan's street games) into addons/street_kit/.
# Canonical copy lives in danbhala/street-kit/tools/; each game keeps a copy in its own tools/.
#
#   tools/update_street_kit.sh 0.2.0   # a specific version
#   tools/update_street_kit.sh         # the latest release
#
# Afterwards: godot --headless --import --path . , check the game, then commit addons/street_kit/.
set -euo pipefail

REPO="danbhala/street-kit"
DEST="addons/street_kit"
ASSET="street-kit.zip"

cd "$(git rev-parse --show-toplevel)"

if [ $# -ge 1 ]; then
  TAG="v${1#v}"
  URL="https://github.com/$REPO/releases/download/$TAG/$ASSET"
else
  TAG="latest"
  URL="https://github.com/$REPO/releases/latest/download/$ASSET"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading Street Kit ($TAG)..."
if [ -n "${STREET_KIT_ZIP:-}" ]; then
  cp "$STREET_KIT_ZIP" "$tmp/$ASSET"   # local zip, for testing a release before publishing
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  if [ "$TAG" = "latest" ]; then
    gh release download -R "$REPO" -p "$ASSET" -D "$tmp"
  else
    gh release download "$TAG" -R "$REPO" -p "$ASSET" -D "$tmp"
  fi
else
  curl -fsSL "$URL" -o "$tmp/$ASSET"
fi

mkdir -p "$tmp/pkg"
unzip -q "$tmp/$ASSET" -d "$tmp/pkg"
[ -f "$tmp/pkg/VERSION" ] || { echo "Downloaded zip has no VERSION file; not installing." >&2; exit 1; }

old="none"
[ -f "$DEST/VERSION" ] && old="$(cat "$DEST/VERSION")"
new="$(cat "$tmp/pkg/VERSION")"

# Keep Godot's generated .import files for assets that still exist, so UIDs stay stable.
if [ -d "$DEST" ]; then
  (cd "$DEST" && find . -name '*.import' -print0) | while IFS= read -r -d '' f; do
    src="${f%.import}"
    if [ -f "$tmp/pkg/$src" ]; then
      mkdir -p "$tmp/pkg/$(dirname "$f")"
      cp "$DEST/$f" "$tmp/pkg/$f"
    fi
  done
fi

rm -rf "$DEST"
mkdir -p "$(dirname "$DEST")"
mv "$tmp/pkg" "$DEST"

echo "Street Kit: $old -> $new in $DEST"
echo "Changes: https://github.com/$REPO/blob/main/CHANGELOG.md"
echo "Next: godot --headless --import --path . , check the game, then commit $DEST."
