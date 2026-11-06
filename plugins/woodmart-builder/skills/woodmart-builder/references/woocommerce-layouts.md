# WooCommerce layouts (Phase 6)

Only for WooCommerce sites. WoodMart's **Layouts** builder (WoodMart → Layouts) replaces WooCommerce
templates with layouts built from WoodMart Woo elements/blocks, shown on pages matched by **conditions**.

## Ask first

Which layouts to build (only those in the design):
- Shop / product archive (also category/tag archives?)
- Single product
- Cart
- Checkout (form + content parts)
- My Account (dashboard, login/register)
- Empty cart, Thank-you (order received)

## Procedure (per layout)

1. `woodmart/list-layout-types` → use its live `type`, `block_categories`, `predefined`,
   `condition_types`. Don't hard-code types.
2. Check `predefined` layouts: a predefined layout close to the design is usually the best start.
3. Show the plan: layout type → sections → elements (from the list below / `gutenberg-list-blocks`
   filtered by the type's `block_categories`).
4. Create the layout **without conditions** (or inactive / Draft), build its content with the Gutenberg
   abilities against its `target_id` (or WPBakery shortcodes in its content — per Phase 1 write path).
5. Read it back, report title / type / ID / edit link.
6. **Do not** call `woodmart/set-layout-conditions` until the user explicitly approves. When they do:
   it **replaces the whole condition set** — read existing conditions first and send all that must
   remain. `[]` unassigns. Don't rely on `is_assigned` over MCP; inspect stored `conditions`.
7. If a layout of the same type is already active, never change it — create a new one and tell the user.

## Typical elements per layout (verify names on the site)

| Layout | Elements |
|--------|----------|
| Shop archive | Archive title/description, breadcrumbs, result count, ordering, products per page/view switcher, filters (active filters, filter buttons, sidebar widgets), Archive products grid, pagination |
| Single product | Product gallery, title, rating, price, short description, add to cart (with swatches), meta, tabs/description/additional info/reviews, upsells, related products, breadcrumbs, navigation, extra content (size guide, compare, wishlist, share) |
| Cart | Cart table, cart totals, coupon, cross-sells, free-shipping progress bar |
| Checkout | Billing/shipping forms, order review, payment methods, coupon, login form |
| My Account | Account navigation, content, login/register form |
| Empty cart / Thank-you | Empty cart message + products, order details / thank-you message |

## Shop settings (Theme Settings → Shop / Product archive / Single product)

Read current → show before → after → apply → verify. Ask about:
- Products per row (desktop/tablet/mobile), products per page, grid gap
- Product hover style ("Products grid" hover: standard, quick, button on image, …)
- Quick view on/off, quick shop
- Swatches (variation swatches on archive and single product; attribute swatch settings are per
  attribute in Products → Attributes — give instructions)
- Wishlist, compare, AJAX add to cart, sticky add to cart, catalog mode
- Sale label / "new" label styles
- Mini cart style (side cart / dropdown)

Product data (products, categories, attributes) is never invented: query existing IDs. If the shop has
no products yet, use WooCommerce sample data only with the user's approval, or build with dynamic queries.
