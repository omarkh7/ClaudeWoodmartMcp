# Design pattern → element map (Phase 5)

## Priority

1. **WoodMart elements** and **WPBakery elements** (or WoodMart Gutenberg `wd/*` blocks on block sites)
2. **WooCommerce** elements / shortcodes
3. **WordPress** widgets / core blocks
4. Nothing fits → **stop and ask** whether to use a custom HTML block. Never silently.

## Two write paths — use the one agreed in Phase 1

### A. WoodMart Gutenberg blocks (`wd/*`)
The `woodmart/*` MCP abilities edit block content. Rules:
- Discover blocks with `woodmart/gutenberg-list-blocks`, then `woodmart/gutenberg-describe-block` for every
  block you author. Use only attributes the describe call returns — never invent them.
- Check `woodmart/gutenberg-search-templates` first: a WoodMart library template that matches a section
  is usually the best start (adjust its texts/images/colors).
- New page: `woodmart/create-content` (status draft) with `block_spec`. Existing non-empty page: read with
  `woodmart/gutenberg-get-content`, change with `woodmart/gutenberg-edit-blocks` (only changed attributes,
  with `expected_content_hash`). Never rebuild a whole page to change part of it.
- Block writes are **queued**: ask the user to keep **WoodMart → Tools → AI Block Queue** open in wp-admin,
  follow the response's `user_instruction`, and poll `woodmart/gutenberg-get-pending-batch` until
  `finalized`. On `conflicted`, re-read and redo.
- Responsive values and styling: use the block's own responsive/style attributes.

### B. WPBakery (shortcodes)
WPBakery stores a page as shortcodes in the post content:
`[vc_row][vc_column width="1/2"][woodmart_title ...][/vc_column][/vc_row]`.
- Check with `mcp-adapter-get-ability-info` whether any create/update ability accepts **raw post content**.
  If yes: write the shortcode content to a Draft page, then read it back.
- If no ability writes raw content: generate the full shortcode for the page (or per section), and give it
  to the user to paste: page → **Backend Editor** → **Classic Mode** (or the text view) → paste → Update
  (keep Draft). Then read the page back via MCP if possible.
- Get exact shortcode tags and parameter names from the site, not from memory: ask the user to open one
  element in WPBakery and copy its shortcode, or inspect an existing page's content via MCP. WoodMart and
  WPBakery versions differ — **verify before using a tag**.
- Spacing/colors/backgrounds go in `css=".vc_custom_...{...}"` Design Options (WPBakery generates these)
  and the element's WoodMart style params, not in Custom CSS.

## Map

Tags in the last column are the usual WPBakery shortcodes — **verify on the site**. On block sites, find the
matching `wd/*` block via `gutenberg-list-blocks`.

| Design pattern | Element | Usual WPBakery tag (verify) |
|----------------|---------|-----------------------------|
| Section / band, full-width background | WPBakery Row (stretch row / full-width, Design Options background, WoodMart row options) | `vc_row` |
| Columns / grid | Row → Columns (widths, responsive offsets/hide in Responsive Options) | `vc_column`, `vc_row_inner`, `vc_column_inner` |
| Heading + subtitle | WoodMart Section title | `woodmart_title` |
| Paragraph / rich text | WoodMart Text block, or WPBakery Text block | `woodmart_text_block`, `vc_column_text` |
| Button / CTA | WoodMart Button | `woodmart_button` |
| Image | WoodMart Image (or WPBakery Single image) | `woodmart_image`, `vc_single_image` |
| Icon / SVG | WoodMart Icon / Image (SVG upload) / Info box icon | `woodmart_image` / `woodmart_info_box` |
| Icon + title + text feature | WoodMart Information box | `woodmart_info_box` |
| Image with text overlay, promo tile | WoodMart Promo banner | `woodmart_promo_banner` |
| Hero slider | WoodMart Slider (Slides post type) | `woodmart_slider` |
| Carousel of banners/cards | WoodMart element with carousel layout (banners carousel, info box carousel) | element-specific `*_carousel` |
| Image gallery / grid / lightbox | WoodMart Images gallery | `woodmart_gallery` |
| Image hotspots / lookbook | WoodMart Image hotspot | `woodmart_image_hotspot` |
| Before/after | WoodMart Compare images | verify |
| Counters / stats | WoodMart Animated counter | `woodmart_counter` |
| Countdown | WoodMart Countdown timer | `woodmart_countdown_timer` |
| Pricing table | WoodMart Pricing tables | `woodmart_pricing_tables` + child |
| Testimonials | WoodMart Testimonials | `woodmart_testimonials` + `testimonial` |
| Team | WoodMart Team member | `woodmart_team_member` |
| Logos strip | WoodMart Brands (product brands) or Images gallery/carousel (static logos) | `woodmart_brands` / `woodmart_gallery` |
| Bullet list with icons | WoodMart List | `woodmart_list` |
| Accordion / FAQ | WoodMart Accordion (or WPBakery Accordion) | `woodmart_accordion` |
| Tabs | WoodMart Tabs (or WPBakery Tabs) | `woodmart_tabs` |
| Timeline / steps | WoodMart Timeline | `woodmart_timeline` |
| Marquee / running text | WoodMart Marquee | verify |
| Social icons | WoodMart Social buttons | `woodmart_social` |
| Instagram feed | WoodMart Instagram | `woodmart_instagram` |
| Map | WoodMart Google Map | `woodmart_google_map` (API key → server side, see SKILL.md Security) |
| Video | WPBakery Video player, or WoodMart video options in banner/image | `vc_video` |
| Blog posts grid | WoodMart Blog | `woodmart_blog` |
| Menu (in-page) | WoodMart Menu / WordPress Custom menu widget | verify |
| Search bar | WoodMart AJAX search | `woodmart_ajax_search` |
| Newsletter | Contact Form 7 (see `cf7-forms.md`), or a mail plugin form if the user has one | `contact-form-7` |
| Contact form | Contact Form 7 | `contact-form-7` |
| Reusable block (header piece, footer, banner) | WoodMart HTML Block, placed with HTML Block element | `html_block` (verify) |
| Spacer / divider | WPBakery Empty space / Separator, or row/column padding | `vc_empty_space`, `vc_separator` |
| Products grid/carousel | WoodMart Products | `woodmart_products` |
| Product categories | WoodMart Product categories | `woodmart_categories` |
| Products with tabs | WoodMart AJAX products tabs | `woodmart_products_tabs` |
| Single product feature | WoodMart Products (by ID), or WooCommerce `[product_page]` | verify |
| Add to cart button | WooCommerce `[add_to_cart]` | `add_to_cart` |
| Sidebar widgets | WordPress widgets in a widget area | — |

## Building a section — checklist

1. Name the section (for comments and the plan): `Home › Hero`.
2. Choose elements from the map; write the plan row: `section → elements → settings used`.
3. Spacing, colors, typography, backgrounds → element/row options (Design Options, WoodMart style,
   Responsive Options). Mobile differences → responsive settings, not CSS.
4. Images → Media Library (descriptive file name, alt text) → reference by attachment ID.
5. Still impossible with settings? Draft the minimal CSS, show it, and add it only to Theme Settings →
   Custom CSS with a section comment (and a custom class on the element via its "Extra class name").
6. Nothing fits at all → ask about a custom HTML block.
