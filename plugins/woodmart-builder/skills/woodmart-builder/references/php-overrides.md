# PHP code and template overrides — handoff format

You **never** edit theme or plugin files. When something needs PHP (a hook, an AJAX handler, a shortcode,
a WooCommerce tweak) or a template override, hand it to the user in this format. Always target the
**child theme** (e.g. `woodmart-child`), never the parent `woodmart` theme (updates would erase it).

## Handoff template

````markdown
### PHP change: <short title>
**Site:** <domain>   **Why:** <what it does, which page/section needs it>

**1. Code**
```php
<?php // remove this line if pasting into an existing file
/**
 * <Title> — added by woodmart-builder, <YYYY-MM-DD>
 * Page/section: <Page › Section>
 */
add_action( 'init', 'wmb_<unique_name>' );
function wmb_<unique_name>() {
    // ...
}
```

**2. Where**
- `wp-content/themes/woodmart-child/functions.php` — paste at the end of the file
  (or the exact override path, e.g. `wp-content/themes/woodmart-child/woocommerce/cart/cart.php`,
  copied from `wp-content/plugins/woocommerce/templates/cart/cart.php` or from the WoodMart parent's
  `woocommerce/` folder if WoodMart already overrides it)

**3. Steps**
1. Back up the file (download a copy) — or take a host snapshot.
2. Appearance → Theme File Editor → select **WoodMart Child** → `functions.php`
   (or via SFTP / host file manager — preferred, because a PHP error can lock you out of the editor).
3. Paste, save.

**4. Test**
- <exact URL / action to check, expected result>
- Check the site still loads front end + wp-admin.

**5. Roll back**
- Remove the pasted block (or restore the backup). If the site shows a critical error, restore the file
  over SFTP / host file manager.
````

## Rules for the code you write

- Prefix all functions/hooks/options with `wmb_` to avoid collisions; wrap in `function_exists` checks
  when declaring helpers.
- Escape output (`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post`), sanitize input
  (`sanitize_text_field`, `absint`, …), check capabilities (`current_user_can`) for admin actions.
- **AJAX handlers**: register `wp_ajax_` (and `wp_ajax_nopriv_` only if needed), verify a nonce
  (`check_ajax_referer`), return with `wp_send_json_success` / `wp_send_json_error`.
- **Secrets** (API keys, tokens): read from a `wp-config.php` constant
  (`define( 'WMB_SERVICE_API_KEY', '...' );` added by the user above "That's all, stop editing!") or a
  server-side option — used only in PHP. Never print them to the page, into JS variables, or into
  `wp_localize_script` data. The browser calls your AJAX endpoint; PHP calls the third-party API.
- Template overrides: copy the original file, change only what's needed, note the template version at the
  top (`@version` header) so the user knows to re-check after WooCommerce/WoodMart updates
  (WooCommerce → Status shows outdated overrides).
- Prefer hooks/filters over full template overrides whenever possible.

## Example: server-side API key + AJAX

```php
add_action( 'wp_ajax_wmb_lookup', 'wmb_lookup' );
add_action( 'wp_ajax_nopriv_wmb_lookup', 'wmb_lookup' );
function wmb_lookup() {
    check_ajax_referer( 'wmb_lookup', 'nonce' );
    if ( ! defined( 'WMB_SERVICE_API_KEY' ) ) {
        wp_send_json_error( 'not configured', 500 );
    }
    $q    = sanitize_text_field( wp_unslash( $_POST['q'] ?? '' ) );
    $resp = wp_remote_get( add_query_arg( 'q', rawurlencode( $q ), 'https://api.example.com/search' ), array(
        'headers' => array( 'Authorization' => 'Bearer ' . WMB_SERVICE_API_KEY ),
        'timeout' => 10,
    ) );
    if ( is_wp_error( $resp ) ) {
        wp_send_json_error( 'request failed', 502 );
    }
    wp_send_json_success( json_decode( wp_remote_retrieve_body( $resp ), true ) );
}

add_action( 'wp_enqueue_scripts', function () {
    // Only the AJAX URL and a nonce reach the browser — never the key.
    wp_register_script( 'wmb-lookup', false, array(), null, true );
    wp_enqueue_script( 'wmb-lookup' );
    wp_add_inline_script( 'wmb-lookup', 'window.wmbLookup=' . wp_json_encode( array(
        'url'   => admin_url( 'admin-ajax.php' ),
        'nonce' => wp_create_nonce( 'wmb_lookup' ),
    ) ) . ';', 'before' );
} );
```
The front-end JS that calls it goes in Theme Settings → Custom JS, sending `action=wmb_lookup`, `nonce`
and `q`.
