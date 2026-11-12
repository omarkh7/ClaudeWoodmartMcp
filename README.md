# woodmart-builder

A Claude skill that turns Claude into a **WoodMart WordPress builder**. It connects to a WoodMart site
through MCP and builds pages from a **Figma design or screenshots**, using only **WoodMart elements,
WPBakery, WooCommerce and WordPress widgets**. It supports **multiple WoodMart sites** side by side
(`woodmart-<domain>` server names).

## What it does

Claude works in gated phases. It asks you a question, waits for your answer and confirms before each step:

1. **Connect the site:** adds the site's MCP server to Claude Desktop (safe merge + backup) and,
   optionally, to Claude Code. It then verifies the connection and checks which page builder and
   abilities the site has.
2. **Design source:** Figma MCP or screenshots (desktop + mobile).
3. **Project questions:** informative or WooCommerce, Framer Motion (Motion) animations, blog, and the page list.
4. **Global settings first:** fonts, colors, buttons, container and header/footer in WoodMart Theme
   Settings. Claude shows before → after and applies only after you approve.
5. **Build pages:** always **WPBakery** (never Gutenberg) with WoodMart elements. Figma spacing is matched
   in each element's Design tab (Desktop/Tablet/Mobile); CSS is used only for glows, grids and resets
   (`wmb-` classes, see `references/spacing-glow-playbook.md`). Element settings are used before any CSS.
   Custom CSS/JS goes only in Theme Settings, forms use Contact Form 7, reusable parts become HTML
   Blocks, and **everything is created as Draft**.
6. **WooCommerce:** WoodMart Layouts for shop, product, cart, checkout and account (kept inactive
   until you approve), plus a review of the shop settings.
7. **Handoff:** a list of everything created, the settings changed, the CSS/JS added, any PHP still
   to add, and open decisions.

Claude never edits theme files, with one exception: with your OK it appends the skill's own snippets
(the Motion enqueue) to `woodmart-child/functions.php` through Claude in Chrome, after backing it up.
Other PHP and template overrides are handed to you with the exact child-theme path, install steps, a
test and a rollback. Claude in Chrome is also used for wp-admin steps MCP can't do (WPBakery Update,
uploads, CF7) and to measure the page against Figma at 1440/1536/768/390.

## Requirements

- **Node.js 18+**, so the MCP bridge can run via `npx` (`@automattic/mcp-wordpress-remote`)
- **Python 3.8+** for the config-merge script
- On each WordPress site:
  - **WoodMart** theme with a child theme active; **WPBakery** if you build with it;
    **WooCommerce** for shops; **Contact Form 7** for forms
  - **WordPress MCP Adapter** plugin, active
    (endpoint `https://<domain>/wp-json/mcp/mcp-adapter-default-server`)
  - An **Application Password** for an admin user (Users → Profile → Application Passwords; needs HTTPS)
- Optional: the **Figma MCP** connector for Figma designs

## Install

### Option 1: Claude Code plugin marketplace (recommended)

```
/plugin marketplace add omarkh7/ClaudeWoodmartMcp
/plugin install woodmart-builder@woodmart-builder
```

Update later with `/plugin marketplace update woodmart-builder`.

### Option 2: Manual install on macOS / Linux

```bash
git clone https://github.com/omarkh7/ClaudeWoodmartMcp.git
cd ClaudeWoodmartMcp
./install.sh          # copies the skill to ~/.claude/skills/woodmart-builder
                      # and the /start-woodmart-mcp command to ~/.claude/commands
```

### Option 3: Manual install on Windows (PowerShell)

```powershell
git clone https://github.com/omarkh7/ClaudeWoodmartMcp.git
cd ClaudeWoodmartMcp
$dest = "$env:USERPROFILE\.claude\skills\woodmart-builder"
if (Test-Path $dest) { Rename-Item $dest "$dest.bak-$(Get-Date -Format yyyyMMdd-HHmmss)" }
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse "plugins\woodmart-builder\skills\woodmart-builder" $dest
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\commands" | Out-Null
Copy-Item "plugins\woodmart-builder\commands\start-woodmart-mcp.md" "$env:USERPROFILE\.claude\commands\"
```

### Option 4: Claude Desktop / claude.ai (upload the skill)

Zip the folder `plugins/woodmart-builder/skills/woodmart-builder` so that the zip contains the
`woodmart-builder/` folder with `SKILL.md` inside. Then upload it in **Claude Desktop or claude.ai →
Settings → Capabilities → Skills**.

## Usage

Start a new session and type:

```
/start-woodmart-mcp
```

Claude shows the 7 steps, then asks you one question at a time and waits for your answer.
(If you installed through the plugin marketplace and another command has the same name, use
`/woodmart-builder:start-woodmart-mcp`.)

You can also just ask in your own words, for example:

> Connect a new WoodMart site and build the home page from my Figma file.

or just `connect woodmart`, `figma to woodmart`, `build woodmart page`, `new woodmart site`.

Claude asks for the site's MCP config, which looks like this:

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

Save that JSON to a file **outside this repo** (e.g. `~/Downloads/site-mcp.json`), then let Claude
run the script, or run it yourself from the skill folder:

```bash
python scripts/add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --dry-run      # preview
python scripts/add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --claude-code  # Desktop + Claude Code
```

The script renames the key to `woodmart-<domain>`, backs up `claude_desktop_config.json`, merges the
new server in (other servers are kept, and another site's entry is never overwritten), validates the
JSON, and never prints the password. Afterwards, **fully quit** Claude Desktop (Cmd+Q on Mac; on
Windows, use the tray icon → Quit) and reopen it.

## Security

- Use a **WordPress Application Password**, not your login password. Create one per computer, and
  revoke it from your WordPress profile when it's no longer needed.
- Real MCP configs and passwords **must never be committed**. The `.gitignore` excludes `*.env`,
  `*.bak*`, `claude_desktop_config*.json` and `*-mcp.json`, but keep your site configs outside the
  repo anyway.
- The skill never puts API keys or tokens in the front end (Custom JS, HTML blocks, page content).
  Secrets go in `wp-config.php` constants or server-side options, used only from PHP/AJAX with nonces.
- All content is created as **Draft**. Publishing and layout assignment always need your explicit
  approval.

## Repo layout

```
.claude-plugin/marketplace.json          marketplace manifest
plugins/woodmart-builder/
  .claude-plugin/plugin.json             plugin manifest
  commands/start-woodmart-mcp.md         the /start-woodmart-mcp slash command
  skills/woodmart-builder/
    SKILL.md                             workflow (phases + rules)
    references/                          setup, settings, element map, spacing & glow playbook, Gutenberg ability rules (read-only), Woo layouts, CF7, Motion, PHP handoff
    templates/mcp-server-entry.json      placeholder config (no real credentials)
    templates/woodmart-child-motion.php  Motion (Framer Motion) enqueue for woodmart-child/functions.php
    scripts/add-woodmart-server.py       safe Claude Desktop / Claude Code config merge
install.sh                               manual installer for macOS/Linux
```

## License

MIT
