---
name: woodmart-builder
description: "Build WordPress pages on a WoodMart theme site over MCP from a Figma design or screenshots, using WoodMart, WPBakery, WooCommerce and WordPress elements only. Use when the user says things like \"build woodmart page\", \"connect woodmart\", \"connect a woodmart site\", \"figma to woodmart\", \"screenshots to woodmart\", \"new woodmart site\", \"woodmart theme settings\", \"woodmart layouts\", or wants a WPBakery/WoodMart page, blog or WooCommerce shop built from a design. Supports multiple WoodMart sites on different domains."
---

# WoodMart Builder

You build WoodMart sites from a design through the site's MCP server. You work in **gated phases**:
in each phase, ask, **wait for the user's answer**, confirm what you understood, then move on.
Never skip a question, never merge two phases, and never assume an answer.

## Global rules (apply in every phase)

1. **Ask, don't assume.** One phase at a time. If something is unclear, stop and ask.
2. **Active site lock.** Work only on the site confirmed in Phase 1. Start every summary and every
   change preview with `Site: <domain> (server: <server-key>)`. If more than one `woodmart-*`
   server is connected, always call the tools of the confirmed server only.
3. **Show → apply → verify.** Before any change, show exactly what will change. After it, read it
   back through MCP and confirm it took effect.
4. **Back up before modifying.** Before editing existing content or settings, read it and record
   the original value (in the session log you keep for Phase 7).
5. **Draft only.** Every page, post, HTML block, form and layout you create is **Draft** / inactive.
   Never publish, never assign a layout live, never change a published URL without explicit approval.
6. **Live ability docs win.** Use `mcp-adapter-discover-abilities` and `mcp-adapter-get-ability-info`
   before the first use of any write ability. Never guess ability names, setting ids, element ids,
   media ids or product/category ids — look them up.
7. **Secrets never leave the server.** Never echo application passwords, API keys or tokens in chat,
   summaries, files, page content, HTML blocks or Custom JS. See Phase 5 → Security.
8. **No theme-file edits — one exception.** PHP/template changes are handed to the user (see
   `references/php-overrides.md`). The only file you may edit yourself is
   `wp-content/themes/woodmart-child/functions.php`, through Claude in Chrome, for snippets this skill
   ships (e.g. the Motion enqueue in `references/animation.md`) — after showing the code, getting a clear
   yes and backing up the current file content. Never the parent `woodmart` theme or plugins.
9. **WPBakery always, never Gutenberg.** Build every new page, post, HTML block and layout with
   **WPBakery** (shortcodes) + WoodMart WPBakery elements. Never create content with the block editor
   or WoodMart Gutenberg (`wd/*`) blocks, even if the site supports them. If WPBakery isn't active on
   the site, stop and ask the user to install/activate it before building.
10. **Spacing/glow method.** Match Figma with the `references/spacing-glow-playbook.md` method on every
   project: spacing in the Design tab (Desktop/Tablet/Mobile), CSS only for glows, grids and resets,
   `wmb-` class prefix.

## Claude in Chrome (always available)

Claude in Chrome is always enabled for this workflow, so you can operate the site's wp-admin and front
end directly. Load the tools in one `ToolSearch` call (`mcp__claude-in-chrome__*`: tabs_context_mcp,
navigate, computer, read_page, find, form_input, javascript_tool, resize_window, read_console_messages).
The user is already signed in, or signs in themselves — never type passwords.

Use it for:
- **Gaps MCP can't cover:** WPBakery backend editor → **Update** after an MCP content write (compiles
  Design Options CSS — see the playbook §4), Theme Settings fields MCP can't write, media uploads,
  creating CF7 forms, the child `functions.php` snippets allowed by rule 8.
- **Measuring and verifying:** `resize_window` to 1440 / 1536 / 768 / 390 and `javascript_tool` with
  `getBoundingClientRect()` to compare against Figma (playbook §1 and §8); console errors; no
  horizontal scroll.
- **Reading back** what MCP wrote, as it renders on the page.

The global rules still apply in Chrome: show → apply → verify, back up first, Draft only, and ask
before any click that saves, publishes or deletes. Prefer MCP when an ability can do the job; use the
browser for what it can't.

Keep a running **session log** (created items, settings before → after, CSS/JS added, PHP pending,
open decisions). Phase 7 is generated from it.

---

## Phase 1 — Connect the WoodMart site (MCP)

Read `references/mcp-setup.md` now.

1. Ask the user for the site's MCP config (format in `templates/mcp-server-entry.json`). Tell them to
   use a **WordPress Application Password** (Users → Profile → Application Passwords), not their login
   password.
2. Derive a unique server key from the domain: `woodmart-<name>` (e.g. `acmeshop.com` → `woodmart-acmeshop`,
   `northwind.com` → `woodmart-northwind`). Show the key and ask the user to confirm it. Never reuse a key
   that already belongs to another site.
3. Add it to **Claude Desktop** with `scripts/add-woodmart-server.py` (backs up, merges, validates,
   never prints the password). Do **not** paste the password into a shell command line yourself — have
   the script read the config from a file the user saved, from stdin, or from its hidden prompt.
4. Offer to add the same server to **Claude Code** (user scope) — the script does this with
   `--claude-code`.
5. Tell the user to **fully quit and reopen Claude Desktop** (Cmd+Q on macOS; on Windows quit from the
   system-tray icon, not just the window). Manual alternative: Settings → Developer → Edit Config →
   paste → save → restart. Reference: https://modelcontextprotocol.io/docs/develop/connect-local-servers
   For Claude Code, the server is available in a new session (`/mcp` shows its status).
6. **Verify**: call `mcp-adapter-discover-abilities` on the new server, summarize what it can do
   (grouped: content, Gutenberg blocks, theme settings, layouts, media, WooCommerce, other), and confirm
   the site name/URL back to the user. Do not continue until this works. On failure, follow the
   troubleshooting list in `references/mcp-setup.md`.
7. **Capability check** — determine and tell the user:
   - **Page builder:** always **WPBakery** (rule 9). Confirm WPBakery is active (plugins list via MCP
     or Chrome). If it isn't, stop and ask the user to install/activate it. Existing Gutenberg content
     may be read, but nothing new is built with blocks.
   - **Write path:** which abilities can create/edit page content, theme settings, media, layouts.
   - **Gaps:** anything the plan needs that no ability can do (e.g. writing raw WPBakery shortcode
     content, uploading media, creating CF7 forms). For each gap, agree on the fallback now: the user
     does that step in wp-admin from exact instructions you give.

**Gate:** connection verified + builder + write path agreed → Phase 2.

## Phase 2 — Design source

Ask: **Figma MCP or screenshots?**

- **Figma:** check that a Figma MCP server is connected (try its `whoami`/metadata tool). If it isn't
  connected or fails, explain how to add it (Claude Desktop: Settings → Connectors → Figma; Claude Code:
  `/mcp` or `claude mcp add`), and wait. Then ask for the file/frame links — one frame per page,
  desktop + mobile frames if they exist. Use Figma variables/styles as the source for Phase 4 values.
- **Screenshots:** ask the user to attach them, one per page, desktop + mobile if available. Ask for
  any values you can't read reliably from an image (exact fonts, hex colors, spacing).

**Gate:** design source received for every page → Phase 3.

## Phase 3 — Project questions (ask all, wait for all answers)

1. Is the site **informative** or **WooCommerce**?
2. Do you want **animations with Framer Motion**? (On WordPress this is **Motion** from motion.dev, the
   vanilla-JS Framer Motion: enqueued once in `woodmart-child/functions.php`, animation code in Theme
   Settings → Custom JS, light, honoring `prefers-reduced-motion`.) If yes, read
   `references/animation.md` and add the enqueue before building.
3. Is there a **blog**? If yes, the blog archive and single post are built too (WoodMart blog settings
   / layouts).
4. **Page list** — propose the list you see in the design (name, slug, template, source frame) and
   ask the user to confirm or edit it.

**Gate:** all four answered and page list confirmed → Phase 4.

## Phase 4 — Global settings FIRST (mandatory, always ask)

Read `references/global-settings.md` now.

1. Extract fonts, colors, buttons, container width and header/footer style from the design and present
   them as a table; ask the user to confirm or correct each value.
2. Read the **current** values from WoodMart → Theme Settings through MCP (find ids with
   `woodmart/list-theme-settings`, read with `woodmart/get-theme-setting`).
3. Show a **before → after** plan. Apply only after approval. Read back each setting and confirm.
4. Flag settings that a preset override still controls, and settings MCP can't write (give the exact
   admin path instead).

**Gate:** global settings applied and verified (or handed off) → Phase 5.

## Phase 5 — Build pages

Read `references/element-map.md` and `references/spacing-glow-playbook.md` now. Read `references/cf7-forms.md` before the first form and
`references/php-overrides.md` before any PHP. Build **one page at a time**: show the section plan
(section → element), get approval, build, verify, report, then ask before starting the next page.

**Status:** every page, post, HTML block or layout is **Draft**.

**Elements (in this order):**
1. WoodMart WPBakery elements and WPBakery elements — always first (never Gutenberg blocks).
2. WooCommerce elements/shortcodes.
3. WordPress widgets.
4. If nothing fits a section: **stop and ask** whether to build it as a custom HTML block. Never
   do it silently.

- Use the elements' built-in options (WPBakery Design Options, WoodMart style/responsive settings) for
  spacing, colors, typography and backgrounds. Write CSS only when no setting can do it, minimal.
- **Spacing and glows** follow `references/spacing-glow-playbook.md`: add the two global blocks
  (spacing baseline `wmb-sp`, glow layer `wmb-glow`) once per site, put `wmb-sp wmb-<pp>-<name>` on
  every section, set every padding/gap in the Design tab (Desktop/Tablet/Mobile), one CSS block per page,
  then Update the page in the WPBakery backend editor and verify at 1440/1536/768/390.
- Reusable parts (header pieces, footers, banners, repeated CTAs) → WoodMart **HTML Blocks**,
  inserted with the HTML Block element.

**Images:**
- Section/row/column backgrounds → WPBakery row/column background (Design Options) or WoodMart
  background options.
- Inline images and icons → WoodMart Image / SVG / Icon elements.
- **Never** use CSS `::before`/`::after` or custom CSS for background images. The only exception is the
  playbook's gradient glows (`wmb-glow`, `wmb-glow-card`): CSS gradients, never image URLs.
- Upload images to the Media Library with descriptive file names and alt text (or, if MCP can't
  upload, give the user a named list to upload and ask for the attachment IDs).

**CSS and JS:**
- All custom CSS goes only in Theme Settings → Custom CSS (global / desktop / tablet / mobile).
- All custom JS goes only in Theme Settings → Custom JS.
- No inline `<style>`/`<script>` in content, no per-element custom CSS unless the user approves it.
- Comment every block: `/* == Page: Home | Section: Hero == */`. Append; never overwrite existing CSS/JS
  — read the current value first and keep it.

**Forms:** Contact Form 7 only. Write the CF7 markup, create it via MCP if an ability allows it,
otherwise give it to the user to create; **ask for the form ID/shortcode**, then place it.

**Security:**
- API keys, tokens and config values never appear in the front end (no Custom JS, HTML blocks or
  page content).
- Store them server-side (`wp-config.php` constants or a server-side option) and use them only in
  PHP/AJAX handlers with nonces — hand that code over via `references/php-overrides.md`.
- Never write credentials into repo files, logs or chat summaries.

**PHP / overrides:** never edit theme files. Give the full code, the exact location (child theme
`functions.php` or override path like `woodmart-child/woocommerce/...`), step-by-step install, test and
rollback. Always the child theme.

After each page: list the created items (title, type, ID, edit link, Draft), then ask to continue.

**Gate:** every confirmed page built and reviewed → Phase 6 (WooCommerce) or Phase 7.

## Phase 6 — WooCommerce (only if WooCommerce site)

Read `references/woocommerce-layouts.md` now. Build layouts with WPBakery + WoodMart Woo elements
(rule 9). If you set layout conditions through an ability, note that `set-layout-conditions` replaces
the whole condition set (`references/gutenberg-abilities.md` → Layouts).

Ask which WoodMart **Layouts** to build: Shop/product archive, Single product, Cart, Checkout,
My Account, Empty cart / Thank-you (if in the design). Build each from the design with WoodMart Woo
elements, keep it Draft / with no active conditions until the user approves. Then review shop settings
in Theme Settings (product grid, hover style, quick view, swatches) with the same before → after flow.

**Gate:** layouts built and settings reviewed → Phase 7.

## Phase 7 — Review & handoff

Give the user, headed with `Site: <domain>`:

1. Everything created: table of title, type, ID, edit link, status (Draft).
2. Theme Settings changes: setting, before → after.
3. Custom CSS/JS added (by section comment).
4. PHP code still to add (with the location).
5. Open decisions / items needing the user (publishing, layout conditions, forms to create, images to
   replace, anything that couldn't be done over MCP).

## Reference files

| File | Read when |
|------|-----------|
| `references/mcp-setup.md` | Phase 1, and any connection problem |
| `references/global-settings.md` | Phase 4, and before any Theme Settings write |
| `references/element-map.md` | Phase 5 section planning |
| `references/spacing-glow-playbook.md` | Phase 5, before the first section: Figma spacing, glows, grids, verification |
| `references/gutenberg-abilities.md` | Only for reading existing block content, logos or layout conditions (no new Gutenberg builds) |
| `references/cf7-forms.md` | Before building a form |
| `references/animation.md` | If the user wants Framer Motion / Motion animations |
| `references/php-overrides.md` | Before handing over any PHP / template override |
| `references/woocommerce-layouts.md` | Phase 6 |
| `templates/mcp-server-entry.json` | Showing the user the config format |
| `templates/woodmart-child-motion.php` | Motion enqueue snippet for `woodmart-child/functions.php` |
| `scripts/add-woodmart-server.py` | Adding a site to Claude Desktop / Claude Code |
