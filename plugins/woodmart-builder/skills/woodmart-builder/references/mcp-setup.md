# Connecting a WoodMart site over MCP

## Requirements on the WordPress site

- WordPress with the **MCP Adapter** plugin active (WordPress/mcp-adapter). It exposes the default
  server at `https://<domain>/wp-json/mcp/mcp-adapter-default-server`.
- WoodMart theme (child theme active), WPBakery if the site uses it, WooCommerce if it's a shop.
- A user with Administrator role and an **Application Password**:
  Users → Profile → Application Passwords → name it e.g. `claude-mcp` → Add → copy the 24-char value
  (shown once). Requires HTTPS. Revoke it there at any time.

## Requirements on the computer

- Node.js 18+ (`node -v`, `npx -v`). The bridge runs as `npx -y @automattic/mcp-wordpress-remote@latest`.
- Python 3.8+ for `scripts/add-woodmart-server.py`.

## Config format

```json
{
  "mcpServers": {
    "woodmart": {
      "command": "npx",
      "args": ["-y", "@automattic/mcp-wordpress-remote@latest"],
      "env": {
        "WP_API_URL": "https://example.com/wp-json/mcp/mcp-adapter-default-server",
        "WP_API_USERNAME": "admin",
        "WP_API_PASSWORD": "<application password>"
      }
    }
  }
}
```

## Naming (multi-site)

Rename the key `woodmart` → `woodmart-<name>` where `<name>` comes from the domain:

| Domain | Key |
|--------|-----|
| `acmeshop.com` | `woodmart-acmeshop` |
| `www.northwind.com` | `woodmart-northwind` |
| `shop.example.co.uk` | `woodmart-shop-example` |

Lowercase, `a-z 0-9 -` only. If the key already exists for a **different** URL, pick another name
(e.g. add `-staging`). Never overwrite another site's entry.

## Adding to Claude Desktop — script (preferred)

The user saves the config they received to a local file **outside the repo** (or pastes it on stdin).
Run from the skill folder:

```bash
# from a saved file (recommended)
python scripts/add-woodmart-server.py --from-file ~/Downloads/site-mcp.json

# preview only
python scripts/add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --dry-run

# also add to Claude Code (user scope)
python scripts/add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --claude-code

# interactive: asks URL + username, reads the password hidden
python scripts/add-woodmart-server.py --interactive --claude-code
```

Use `python3` on macOS/Linux, `py` or `python` on Windows. Options: `--name woodmart-x` (override the
derived key), `--replace` (update an existing entry **for the same URL**), `--config-path` (non-standard
location), `--no-desktop` (Claude Code only).

The script: finds the config per OS, backs it up to `claude_desktop_config.json.bak-YYYYMMDD-HHMMSS`,
merges into `mcpServers` keeping all other servers and keys, validates the JSON, writes atomically, and
prints a masked summary (password never printed). Afterwards delete the saved config file or keep it in a
password manager.

Config locations:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  (Microsoft Store install: `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`
  — the script detects both and asks for `--config-path` if both exist)
- Linux (unofficial builds): `~/.config/Claude/claude_desktop_config.json`

## Adding to Claude Desktop — manual

Settings → Developer → Edit Config → open `claude_desktop_config.json` → add the renamed entry inside
the existing `"mcpServers": { ... }` (comma between entries) → save → **fully quit** and reopen Claude
(macOS: Cmd+Q; Windows: right-click the tray icon → Quit). Docs:
https://modelcontextprotocol.io/docs/develop/connect-local-servers

## Adding to Claude Code

Preferred: `--claude-code` in the script (calls `claude mcp add-json <key> <json> --scope user` without
going through shell history). Manual equivalent — note this puts the password in shell history, so
clear it afterwards:

```bash
claude mcp add woodmart-acmeshop --scope user \
  -e WP_API_URL=https://acmeshop.com/wp-json/mcp/mcp-adapter-default-server \
  -e WP_API_USERNAME=admin \
  -e WP_API_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx' \
  -- npx -y @automattic/mcp-wordpress-remote@latest
```

Check with `claude mcp list` / `/mcp`. Remove with `claude mcp remove woodmart-acmeshop --scope user`.

## Verifying

1. Call `mcp-adapter-discover-abilities` on the new server.
2. Group the abilities for the user (content, Gutenberg blocks, theme settings, layouts, media,
   WooCommerce, other) and point out which ones Phase 4–6 will rely on.
3. Confirm the site: read the site name/URL (e.g. via a site-info/settings ability, or a
   `woodmart/search-content` call that returns permalinks) and show it back: "Connected to
   **Site Name** — https://domain". Ask the user to confirm it is the right site.
4. Capability check (SKILL.md Phase 1 step 7): WPBakery active, write path, gaps (Claude in Chrome covers wp-admin gaps).

Useful adapter tools: `mcp-adapter-discover-abilities`, `mcp-adapter-get-ability-info`
(call before first use of a write ability), `mcp-adapter-execute-ability` (`ability_name`, `parameters`).

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Server doesn't appear | Claude Desktop fully quit and reopened? JSON valid (script validates; manual edits often miss a comma)? |
| `npx` not found / spawn error | Node.js installed and on PATH (`node -v`). On Windows, if Claude Desktop still can't spawn it, set `"command"` to the full path of `npx.cmd` (e.g. `C:\\Program Files\\nodejs\\npx.cmd`). |
| 404 / no route | `WP_API_URL` must end with `/wp-json/mcp/mcp-adapter-default-server`; MCP Adapter plugin active; permalinks not "Plain" (Settings → Permalinks → Save once). |
| 401 / 403 | Application password correct (spaces are fine), username is the login name not the display name, user is Administrator, a security plugin/firewall (Wordfence, Cloudflare, host WAF) isn't blocking `/wp-json/` or Basic auth headers. |
| Application Passwords section missing | Site not on HTTPS, or disabled by a security plugin. |
| Connected but no `woodmart/*` abilities | WoodMart version too old for MCP abilities, or the abilities are disabled; content work then needs a different write path — tell the user. |
| Logs | Claude Desktop: Settings → Developer → server → logs (macOS `~/Library/Logs/Claude/mcp-server-*.log`, Windows `%APPDATA%\Claude\logs\`). Never paste logs containing the password into chat. |
