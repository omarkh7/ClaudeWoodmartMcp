# Global settings checklist (Phase 4)

Global settings are applied **before** any page is built, so pages inherit them instead of each element
being styled by hand.

## Procedure

1. **Extract** from the design (Figma variables/text styles/color styles, or screenshots) into the table
   below. Mark each value as `from design` or `guessed — confirm`.
2. **Ask the user to confirm** every row.
3. **Find setting ids** with `woodmart/list-theme-settings` (search by section/keyword). Never guess ids.
4. **Read current values** with `woodmart/get-theme-setting` right before writing. Respect `writable`,
   `value_format`, `options`, `current_value`, `has_preset_overrides`.
5. **Show the plan**: `setting id | label | current → new`. Wait for approval.
6. **Apply** with `woodmart/update-theme-setting`, then **read back** each value.
7. If `has_preset_overrides` is true, the visible value may still come from a Theme Settings preset —
   report it and ask whether to edit the preset in wp-admin; don't retry blindly.
8. Settings that can't be written over MCP → give exact admin path + value.
9. Log every change (before → after) for Phase 7.

## What to collect

### Typography (Theme Settings → Typography)
| Item | Notes |
|------|-------|
| Text font (body) | family, weight, size, line-height, color |
| Primary font / title font (headings) | family, weights used, H1–H6 sizes desktop/mobile |
| Secondary font | used for accents/labels in WoodMart |
| Entities / widget titles / header (menu) font | family, size, weight, letter-spacing, transform |
| Font source | Google Fonts (pick weights actually used) or custom upload (Theme Settings → Typography → Custom fonts; user uploads font files) |

### Colors (Theme Settings → Styles and colors)
| Item | Notes |
|------|-------|
| Primary color | main brand color |
| Secondary color | |
| Text / title colors | body text, headings |
| Link color + hover | |
| Page / site background | body background; boxed layout background if used |
| Form field style | border, radius |
| Dark/light scheme | per-area color scheme (header, footer) |

### Buttons (Theme Settings → Buttons)
| Type | Background / hover | Text / hover | Radius | Padding / height | Style (flat/3D/bordered) |
|------|--------------------|--------------|--------|------------------|---------------------------|
| Default buttons | | | | | |
| Accent buttons | | | | | |
| Shop / Add to cart | | | | | |

### General layout (Theme Settings → General / Layout)
- Site width / container width (e.g. 1222 px default → design value), boxed vs full-width.
- Responsive breakpoints are fixed by the theme; design to its tablet/mobile breakpoints.
- Page title area (on/off, style), breadcrumbs.

### Header & footer
- Header: built in **WoodMart → Header Builder** (structure, sticky, logo, menu, search, cart, account).
  Logo replacement can use `woodmart/replace-header-logo` (needs a media attachment ID). Header
  structure changes usually need wp-admin — give step-by-step instructions.
- Footer: WoodMart footer settings, typically an **HTML Block** selected in Theme Settings → Footer.
  Build the footer content as an HTML Block (Draft) and ask before assigning it.

### Other global items worth asking about
- Favicon, 404 page, preloader, scroll-to-top, cookie notice.
- Blog defaults (if blog): archive design, columns, single post layout.
- Shop defaults (if WooCommerce): see `woocommerce-layouts.md`.

## Custom CSS / JS fields

These also live in Theme Settings (find exact ids via `list-theme-settings`; typically global, desktop,
tablet, mobile-landscape and mobile CSS, plus custom JS / "on document ready" JS). Before adding:
read the current value, append your commented block, show the diff, write, read back.
