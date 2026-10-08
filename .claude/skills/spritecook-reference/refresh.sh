#!/usr/bin/env bash
# Snapshot SpriteCook's free endpoints so the reference can be checked for drift.
# Spends no credits: only list/read calls. Needs SPRITECOOK_API_KEY; never prints it.
# Usage: refresh.sh [out_dir]   (default: a new temp dir)
set -euo pipefail
out=${1:-$(mktemp -d)}
mkdir -p "$out"
auth="Authorization: Bearer ${SPRITECOOK_API_KEY:?set SPRITECOOK_API_KEY}"
api=https://api.spritecook.ai

for p in models character-workflows credits; do
  curl -sSf -H "$auth" "$api/v1/api/$p" -o "$out/$p.json"
done

mcp() {
  curl -sSf -X POST "$api/mcp/" -H "$auth" -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' -d "$1"
}
mcp '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"refresh","version":"1"}}}' > "$out/mcp-initialize.json"
mcp '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' > "$out/mcp-tools.json"
mcp '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_tileset_options","arguments":{}}}' > "$out/tileset-options.json"

for p in llms.txt sitemap.xml; do
  curl -sSfL "https://www.spritecook.ai/$p" -o "$out/$p" || echo "could not fetch $p" >&2
done

echo "Snapshot in $out. Compare with SKILL.md and references/, then update both."
