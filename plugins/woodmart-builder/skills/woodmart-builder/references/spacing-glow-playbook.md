# WoodMart + WPBakery: matching Figma spacing & glows

How to match a Figma page exactly in WoodMart (WPBakery builder): widget spacing, section glows,
card glows, equal-height cards and grids. Read this in Phase 5 before building the first section,
and use it on every project.

## Naming (project-neutral)

All classes use the prefix **`wmb-`** (woodmart-builder), the same prefix the PHP handoff uses (`wmb_`).

| Class | Put it on | Purpose |
|---|---|---|
| `wmb-sp` | every rebuilt section | removes WPBakery's hidden spacing defaults (section 3) |
| `wmb-glow` | sections with a Figma glow | full-bleed CSS glow layer (section 5.1) |
| `wmb-glow-card` | inner row that is a card | glow clipped inside the card (section 5.3) |
| `wmb-eyebrow`, `wmb-kicker` | small labels above headlines | line-height / margin reset |
| `wmb-<pp>-<name>` | page-specific sections and rows | `<pp>` = 2-letter page prefix (`hm` Home, `ab` About, `sv` Services…), e.g. `wmb-hm-hero`, `wmb-ab-cards` |

In the snippets below, `wmb-xx-…` means "replace `xx` with the page prefix".

---

## 0. The rules

1. **Spacing goes in the Design tab, not CSS.** Each element's Design tab has **Desktop / Tablet /
   Mobile** fields. Desktop is WPBakery Design Options; Tablet and Mobile are WoodMart's responsive
   spacing. Anyone can then see and change it in the editor.
2. **CSS is only for what the editor can't do:** glows, equal-height cards, CSS grids, flex rows
   (side by side + bottom aligned), and resetting theme defaults.
3. **Never put `!important` spacing in CSS on an element that also has Design tab spacing.** The CSS
   wins and the Design tab silently stops working.
4. **One CSS block per page** in Theme Settings → Custom CSS, scoped by the page's `wmb-xx-…` classes,
   so pages can't affect each other. The two global blocks (sections 3 and 5.1) are added once per site.
5. **Back up first.** WordPress keeps a revision of each page save; copy the current Custom CSS value
   into the session log before every change.

Breakpoints (WoodMart's own):

| Name | Width | Where it is set |
|---|---|---|
| Desktop | ≥ 1025px | Design Options (Desktop tab) |
| Laptop | 1025–1399px | Global CSS (type scaled to ~85%) if the design needs it |
| Tablet | ≤ 1024px | Design tab → Tablet |
| Mobile | ≤ 767px | Design tab → Mobile |

---

## 1. Measure the Figma page first

For every section in the Figma frame, write down:

- **Section padding:** section top → first element, last element → section bottom.
- **Gaps between elements:** label → headline, headline → text, header → cards, … Figma auto-layout
  `gap` values give these directly.
- **Fixed sizes:** card width × height, column widths (e.g. 526 + 80 gap + rest), max text widths
  (e.g. 620, 720).
- **Glows:** for every blurred ellipse: x, y, width, height, fill colour + opacity, layer blur (section 5).

Then open the live page at a **1440px** viewport (Claude in Chrome → `resize_window`) and measure the
same things with `getBoundingClientRect()` (`javascript_tool`). The differences are the to-do list.

A common Figma rhythm: sections 120 top/bottom, header → content 64 or 72, label → headline 56–72,
card gap 24. Always use the design's own numbers.

---

## 2. Why WPBakery spacing never matches Figma (hidden defaults)

These add space that isn't in Figma. Remove them first, or every number will be off.

| Default | Size | Where |
|---|---|---|
| Widget bottom margin | 30–35px | Every WoodMart/WPBakery widget (title, text, list, separator, button) |
| Section padding | 35px top | `.vc_section` with a background (`vc_section-has-fill`) |
| Column top padding | 35px | Columns inside rows that have a background |
| Column side padding | 15px each side | Every column (`.vc_column-inner`) |
| Row side margins | −15px | Every row (cancels the column padding) |
| Section side margins on mobile | −15px | Sections overflow the screen on phones |
| Gap rows (`gap="20"`, `gap="30"`) | extra padding + negative margins | Column containers |
| Full-width (stretched) sections | columns keep 15px padding | Content sits 15px further in than boxed sections |

---

## 3. Spacing baseline (global CSS, add once per site)

Add `wmb-sp` to every section you build (Section → General → Extra class name). This CSS removes the
defaults above, so every gap comes only from the Design tab.

```css
/* == Global | Spacing baseline (.wmb-sp on a section) == */
.vc_section.wmb-sp { margin-top: 0 !important; margin-bottom: 0 !important; }
.wmb-sp .wpb_wrapper > * { margin-bottom: 0; }                      /* widget 30px default off (no !important, so the Design tab still wins) */
.wmb-sp .wpb_wrapper > :last-child { margin-bottom: 0 !important; } /* last widget in a column never adds space */
.wmb-sp .vc_row-has-fill > .vc_column_container > .vc_column-inner { padding-top: 0; } /* 35px column top padding off */
.wmb-sp .wmb-eyebrow { margin-bottom: 0 !important; }
.wmb-sp .wmb-eyebrow li, .wmb-sp .wmb-eyebrow .wd-list-content { line-height: 14px !important; }
.wmb-sp .wmb-kicker, .wmb-sp .wmb-kicker p { line-height: 12px !important; }
/* Tablet/phone side gutters: no -15px overflow, 40px / 20px edges */
@media (max-width: 1024px) { .vc_section.wmb-sp { margin-left: 0 !important; margin-right: 0 !important; padding-left: 40px !important; padding-right: 40px !important; } }
@media (max-width: 767px)  { .vc_section.wmb-sp { padding-left: 20px !important; padding-right: 20px !important; } }
```

Adjust the eyebrow/kicker line-heights and the 40/20 gutters to the design.

Two consequences:

- Because of the `:last-child` rule, **space below the last widget of a column is set on the row**
  (row Design tab → margin-bottom), not on the widget.
- Space **between** widgets: a **margin-top on the lower widget** (e.g. headline margin-top 56), or a
  margin-bottom on the upper widget if it isn't the last one.

Full-width (stretched) sections need their content on the same edge as boxed sections:

```css
.wmb-xx-hero .vc_column_container > .vc_column-inner { padding-left: 0; padding-right: 0; }
```

---

## 4. Setting spacing in the Design tab

For each element: settings (pencil) → **Design Options**. At the top: **Desktop / Tablet / Mobile**.

1. **Desktop:** the Figma value (e.g. section padding 120 / 120).
2. **Tablet:** only where it differs (e.g. 96 / 96).
3. **Mobile:** same (e.g. 72 / 72).
4. Save the element, then **Update** the page.

Empty Tablet/Mobile fields inherit Desktop.

| Spacing | Element | Field |
|---|---|---|
| Section top/bottom | Section | Padding top / bottom |
| Gap between rows (header → cards) | The upper row | Margin bottom |
| Label → headline, headline → text | The lower widget | Margin top |
| Card inner padding | Inner row (the card) | Padding all 4 sides |
| Gap when columns stack on tablet/phone | The upper column | Tablet / Mobile margin bottom |

Starting values (replace with the design's):

| Item | Desktop | Tablet | Mobile |
|---|---|---|---|
| Hero section (header overlapping the hero) | header height + top gap / 120 | ~160 / 96 | ~130 / 72 |
| Normal section | 120 / 120 | 96 / 96 | 72 / 72 |
| Label → headline | 56–72 | same | 32 |
| Header row → content | 64 or 72 | same | 40–48 |
| Card padding | 40 | 40 | 24 |
| Stacked columns gap | — | 24–40 | 24–40 |

### Setting it by MCP / REST instead of the editor

- Desktop values live in the shortcode's `css` attribute:
  `css=".vc_custom_1794…{padding-top: 120px !important;padding-bottom: 120px !important;}"`.
  **This CSS is compiled only when the page is saved in the WPBakery backend editor.** A REST/MCP save
  alone doesn't rebuild it → after an MCP write, open the page in WPBakery and click **Update**
  (Claude in Chrome can do this; see SKILL.md → Claude in Chrome).
- Tablet/Mobile values live in `responsive_spacing="…"`, **plain base64** of:
  ```json
  {"param_type":"woodmart_responsive_spacing","selector_id":"<same as woodmart_css_id>","shortcode":"vc_section","data":{"tablet":{"padding-top":"96px"},"mobile":{"padding-top":"72px"}}}
  ```
  - `selector_id` must equal the element's `woodmart_css_id` attribute.
  - **Do not URL-encode it.** An encoded `==` (`%3D%3D`) silently breaks it: only values whose base64
    had no `=` padding work.
  - WoodMart outputs these at render as `.wd-rs-<id>` rules, so no re-save is needed for them.
- For columns, WoodMart applies the responsive margin to `.wd-rs-<id> > .vc_column-inner`.
- Old Tablet/Mobile values may already exist and may have been hidden by `!important` CSS. When you
  remove that CSS they start to apply — check every element's responsive values before deleting CSS.

---

## 5. Section glows (pure CSS from Figma, no images)

Figma glows are blurred ellipses (fill + opacity + Layer blur). Don't export them as images: images end
at their own edge, so wide screens get hard bands at the sides. Rebuild them in CSS.

> This is the one allowed use of `::before`/`::after` for backgrounds: gradients only, never image URLs.

### 5.1 Global glow layer (add once per site)

`wmb-glow` on a section turns its `::before` and `::after` into 2 large blurred layers behind the
content (one per Figma blur value).

```css
/* == Global | Glow layer (.wmb-glow on a section) == */
.wpb-content-wrapper:has(> .vc_section.wmb-glow) { isolation: isolate; }   /* keeps z-index:-1 inside the page */
.vc_section.wmb-glow { position: relative; overflow: visible !important; background-image: none !important; }
.vc_section.wmb-glow::before, .vc_section.wmb-glow::after {
  content: ""; display: block; position: absolute; top: 0; left: 50%;
  width: 2880px; height: 1200px; margin-left: -1440px;          /* 2x the 1440 design, centred */
  background-repeat: no-repeat; pointer-events: none; z-index: -1;
  transform: scale(var(--wmb-glow-s, 1)); transform-origin: 50% 0;
}
.vc_section.wmb-glow::before { filter: blur(120.5px); }   /* Figma layer blur #1 */
.vc_section.wmb-glow::after  { filter: blur(97.5px); }    /* Figma layer blur #2 */
.vc_section.wmb-glow > * { position: relative; z-index: 1; }
@media (max-width: 1024px) { .vc_section.wmb-glow { --wmb-glow-s: 0.85; } }
@media (max-width: 767px)  { .vc_section.wmb-glow { --wmb-glow-s: 0.65; } }
```

Set the two `blur()` values to the design's two most common Layer blur values. Why this setup:

- **2880px layer:** the 1440 design sits at x 720–2160, so no ellipse touches the layer edge and the
  blur fades freely past the screen edges (no side bands at 1536 / 1920).
- **No `overflow` clip:** the glow can float behind the next section, as in Figma.
- **`isolation: isolate` on the page wrapper:** `z-index: -1` stays above the page background.
- Remove any Design Options background images from the section (`wmb-glow` forces `background-image: none`).
- If the design frame isn't 1440 wide, use 2× its width and half of that as `margin-left`.

### 5.2 Converting each Figma ellipse

| Figma | CSS |
|---|---|
| W, H | radii: `rx = W / 2`, `ry = H / 2` |
| X (relative to the page frame) | centre x = `X + W/2 + 720` |
| Y (relative to the **section's** top) | centre y = `Y + H/2` |
| Fill `#E3466C` at 50% | `rgba(227, 70, 108, 0.5)` |
| Layer blur | the pseudo-element with that blur (`::before` / `::after`) |

One `radial-gradient` per ellipse. The `99.5% → 100%` stop makes a solid ellipse; the blur softens it:

```css
radial-gradient(RXpx RYpx at CXpx CYpx, rgba(R, G, B, A) 99.5%, transparent 100%)
```

Ellipses with the same blur go in the same pseudo-element, comma-separated. Example (hero with a teal
ellipse and a pink circle, both blur 97.5):

```css
.vc_section.wmb-xx-hero.wmb-glow::before { background-image: none; }
.vc_section.wmb-xx-hero.wmb-glow::after {
  background-image:
    radial-gradient(280.147px 297.956px at 957px 142px, rgba(73, 201, 236, 0.44) 99.5%, transparent 100%),
    radial-gradient(329.5px 329.5px at 2049.5px 336.5px, rgba(227, 70, 108, 0.5) 99.5%, transparent 100%);
}
```

Stacking: later sections paint over earlier glows, matching Figma's layer order. If a glow must sit
**over** the next section, give that next section `position: relative; z-index: 1`.

### 5.3 Card glows (clipped inside a card)

For a glow inside a card (e.g. Figma circle r160 at 99,39 in the card, blur 80, opacity .35):

```css
.wmb-xx-cards .wmb-glow-card { position: relative; overflow: hidden; background-image: none !important; }
.wmb-xx-cards .wmb-glow-card::before {
  content: ""; display: block; position: absolute;
  left: -61px; top: -121px;          /* centre (99,39) minus radius 160 */
  width: 320px; height: 320px; border-radius: 50%;
  filter: blur(80px); opacity: .35; pointer-events: none; z-index: 0;
}
.wmb-xx-cards > .wpb_column:nth-child(1) .wmb-glow-card::before { background: #FF9C01; }
.wmb-xx-cards > .wpb_column:nth-child(2) .wmb-glow-card::before { background: #E3466C; }
.wmb-xx-cards > .wpb_column:nth-child(3) .wmb-glow-card::before { background: #49C9EC; }
.wmb-xx-cards .wmb-glow-card > .wpb_column { position: relative; z-index: 1; }   /* text above the glow */
```

`left` = centre x − radius, `top` = centre y − radius. Use the design's colours.

---

## 6. Layout the Design tab can't do (CSS)

### 6.1 Equal-height cards (text at the bottom)

WPBakery cards grow with their text. Put the row in a CSS grid, give each card a fixed height, and push
the content apart with flex.

```css
.vc_row.wmb-xx-cards { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; margin: 0 !important; }
.vc_row.wmb-xx-cards::before, .vc_row.wmb-xx-cards::after { display: none; }       /* WPBakery clearfix would become grid items */
.wmb-xx-cards > .wpb_column { width: auto !important; float: none; padding: 0 !important; }
.wmb-xx-cards > .wpb_column > .vc_column-inner { padding: 0 !important; height: 100%; }
.wmb-xx-cards > .wpb_column > .vc_column-inner > .wpb_wrapper { height: 100%; }
.wmb-xx-cards .vc_row.vc_inner { display: flex; box-sizing: border-box; height: 440px; margin: 0 !important; }  /* Figma card height */
.wmb-xx-cards .vc_inner > .wpb_column { width: 100% !important; float: none; }
.wmb-xx-cards .vc_inner > .wpb_column > .vc_column-inner { padding: 0 !important; height: 100%; }
.wmb-xx-cards .vc_inner .wpb_wrapper { display: flex; flex-direction: column; height: 100%; }
.wmb-xx-cards .vc_inner .wpb_wrapper > :first-child { margin-bottom: auto !important; }  /* number on top, the rest at the bottom */
@media (max-width: 1024px) { .vc_row.wmb-xx-cards { grid-template-columns: 1fr; gap: 20px; } .wmb-xx-cards .vc_row.vc_inner { height: auto; min-height: 340px; } }
@media (max-width: 767px)  { .wmb-xx-cards .vc_row.vc_inner { min-height: 300px; } }
```

Card padding (e.g. 40 desktop / 24 mobile) stays in the inner row's Design tab.

### 6.2 2 × 2 grid from 2 WPBakery columns (keeps reading order on phones)

If column 1 = cards 01, 03 and column 2 = cards 02, 04, flatten them with `display: contents` and fix
the order:

```css
.vc_row.wmb-xx-pgrid { display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; margin: 0 !important; }
.vc_row.wmb-xx-pgrid::before, .vc_row.wmb-xx-pgrid::after { display: none; }
.wmb-xx-pgrid > .wpb_column, .wmb-xx-pgrid > .wpb_column > .vc_column-inner, .wmb-xx-pgrid > .wpb_column > .vc_column-inner > .wpb_wrapper { display: contents; }
/* their clearfix pseudo-elements would otherwise take grid cells */
.wmb-xx-pgrid > .wpb_column::before, .wmb-xx-pgrid > .wpb_column::after,
.wmb-xx-pgrid > .wpb_column > .vc_column-inner::before, .wmb-xx-pgrid > .wpb_column > .vc_column-inner::after { display: none !important; }
.wmb-xx-pgrid > .wpb_column:nth-child(1) .wmb-xx-pcard:nth-child(1) { order: 1; }
.wmb-xx-pgrid > .wpb_column:nth-child(2) .wmb-xx-pcard:nth-child(1) { order: 2; }
.wmb-xx-pgrid > .wpb_column:nth-child(1) .wmb-xx-pcard:nth-child(2) { order: 3; }
.wmb-xx-pgrid > .wpb_column:nth-child(2) .wmb-xx-pcard:nth-child(2) { order: 4; }
@media (max-width: 767px) { .vc_row.wmb-xx-pgrid { grid-template-columns: 1fr; gap: 20px; } }
```

### 6.3 Header row: headline + gap + intro, bottom-aligned

```css
@media (min-width: 1025px) {
  .vc_row.wmb-xx-head { display: flex !important; flex-wrap: nowrap; align-items: flex-end; }
  .vc_row.wmb-xx-head::before, .vc_row.wmb-xx-head::after { display: none; }
  .wmb-xx-head > .wpb_column:first-child { width: auto !important; flex: 0 0 780px; }            /* Figma left width */
  .wmb-xx-head > .wpb_column:first-child > .vc_column-inner { padding-right: 0 !important; }
  .wmb-xx-head > .wpb_column:last-child { width: auto !important; flex: 1 1 0; min-width: 0; }
  .wmb-xx-head > .wpb_column:last-child > .vc_column-inner { padding-left: 80px !important; }   /* Figma gap */
}
```

Use `flex: 0 0 auto` plus `white-space: nowrap` on the title when the headline must keep its natural width.

### 6.4 3 columns with inner gutters (Figma "steps")

```css
@media (min-width: 1025px) {
  .vc_row.wmb-xx-steps { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; margin: 0 !important; }
  .vc_row.wmb-xx-steps::before, .vc_row.wmb-xx-steps::after { display: none; }
  .wmb-xx-steps > .wpb_column { width: auto !important; float: none; padding: 0 !important; }
  .wmb-xx-steps > .wpb_column > .vc_column-inner { padding: 0 !important; }
  .wmb-xx-steps > .wpb_column:nth-child(1) > .vc_column-inner { padding-right: 40px !important; }
  .wmb-xx-steps > .wpb_column:nth-child(2) > .vc_column-inner { padding-left: 40px !important; padding-right: 40px !important; }
  .wmb-xx-steps > .wpb_column:nth-child(3) > .vc_column-inner { padding-left: 40px !important; }
}
@media (max-width: 1024px) { .wmb-xx-steps > .wpb_column { width: 100% !important; float: none; } }
```

The stacked gap (e.g. 40) on tablet/mobile goes in columns 2 and 3 → Design tab → Tablet margin-top.

---

## 7. Step-by-step for a new page

1. **Measure Figma** (section 1): padding, gaps, sizes, glow ellipses.
2. **Name things.** Pick a 2-letter page prefix and add classes:
   - every section: `wmb-sp wmb-xx-<name>`, plus `wmb-glow` on sections with a glow
   - rows that need CSS layout: `wmb-xx-head`, `wmb-xx-cards`, `wmb-xx-pgrid`, `wmb-xx-steps`, …
3. **Remove old backgrounds:** delete Design Options glow images from sections that get `wmb-glow`.
4. **Enter spacing in the Design tab** for every section, row, widget and card (section 4).
5. **Add one CSS block** in Theme Settings → Custom CSS, titled
   `/* == Page: <Name> (<id>) | Figma <node> == */`, containing only:
   glow gradients (5.2), card glows (5.3), grids / equal heights / flex rows (6), stretched-section
   edge fix (end of 3).
6. **Update the page in the WPBakery backend editor** (compiles Desktop Design Options CSS).
7. **Verify** (section 8).
8. **Log** what changed (page, classes, values) in the session log for the Phase 7 handoff.

---

## 8. Verification checklist

Check at **1440, 1536 (or 1920), 768 and 390** wide (Claude in Chrome → `resize_window`):

- [ ] Section padding and gaps equal the Figma values (measure with `getBoundingClientRect()`, not by eye).
- [ ] Content left edges line up across full-width and boxed sections (same x as Figma, e.g. 80px at 1440).
- [ ] Cards in a row are exactly the same height.
- [ ] Glows: right colour and position, soft edges, no hard bands at wide-screen sides, not cut off at the section bottom.
- [ ] No horizontal scroll: `document.documentElement.scrollWidth === document.documentElement.clientWidth`.
- [ ] Phone: reading order is correct and stacked columns have gaps.
- [ ] Change one value in the Design tab and confirm it shows on the page (proves no CSS overrides it), then change it back.

---

## 9. Problems and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Design tab value has no effect | A CSS rule with `!important` on the same element | Delete the CSS rule, keep the value in the Design tab |
| Tablet/Mobile value has no effect (set by script) | `responsive_spacing` URL-encoded, or `selector_id` ≠ `woodmart_css_id` | Store plain base64 and match the ids (section 4) |
| Desktop Design Options missing on the live page | Page saved by REST/MCP only | Open in the WPBakery backend editor → Update |
| An HTML block looks different on one page only | Its `vc_custom_<id>` collides with an id on that page | Give the block new unique Design Options ids and re-save it |
| Glow ends in a hard vertical band on wide screens | Glow was a 1440px image | Use the 2880px CSS glow layer |
| Glow cut off at the section bottom | `overflow: hidden` on the section | `overflow: visible` (the glow layer CSS does this) |
| Grid has an empty first cell | WPBakery clearfix `::before` became a grid item | `::before, ::after { display: none }` on the row and on `display: contents` wrappers |
| Editor crashes on Background style | Only cover/contain are allowed in that dropdown | Set other sizes in CSS (`background-size: auto !important`) |
| Phones scroll sideways | Sections keep −15px side margins | Baseline: section margins 0 + 40/20 gutters (section 3) |
| A Design Options value shows in the editor but not on the page | Saving an element panel gives it a new `vc_custom` id, compiled only on page Update | Click Update on the page after editing elements |
