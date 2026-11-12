# Animations with Motion (Framer Motion for WordPress)

**Framer Motion** is React-only. Its vanilla-JS version is **Motion** (https://motion.dev, npm package
`motion`) — same team, same `animate` / `inView` / `scroll` / `stagger` API, no React needed. That is
what "Framer Motion" means on a WoodMart/WPBakery site.

Setup has two parts, both done once per site:

1. **Load the library** — enqueued from the child theme's `functions.php` (below). This replaces
   any `import()` / `<script>` tag approach.
2. **The animation code** — in Theme Settings → Custom JS. It uses the global `window.Motion`.

## 1. Enqueue Motion in `woodmart-child/functions.php`

File: `wp-content/themes/woodmart-child/functions.php` (child theme only — never the parent `woodmart`).
The same snippet is in `templates/woodmart-child-motion.php`.

```php
/**
 * Motion (motion.dev) — vanilla-JS Framer Motion. Added by woodmart-builder.
 * Exposes window.Motion (animate, inView, scroll, stagger, ...) on the front end.
 */
if ( ! defined( 'WMB_MOTION_VERSION' ) ) {
	define( 'WMB_MOTION_VERSION', '14.7.1' ); // pinned; bump only after testing
}
add_action( 'wp_enqueue_scripts', 'wmb_enqueue_motion', 20 );
function wmb_enqueue_motion() {
	// Not inside the WPBakery front-end editor (animations would hide content while editing).
	if ( function_exists( 'vc_is_page_editable' ) && vc_is_page_editable() ) {
		return;
	}
	wp_enqueue_script(
		'wmb-motion',
		'https://cdn.jsdelivr.net/npm/motion@' . WMB_MOTION_VERSION . '/dist/motion.js',
		array(),
		WMB_MOTION_VERSION,
		array( 'in_footer' => true, 'strategy' => 'defer' )
	);
}
```

Notes:
- `dist/motion.js` is the UMD build: it defines `window.Motion`. Pin an exact version (check npm,
  choose one at least ~2 weeks old, confirm with the user). Never `@latest`.
- `strategy => defer` needs WordPress 6.3+. On older WordPress, use `true` (in footer) instead of the array.
- To self-host instead of the CDN: download that `motion.js` into `woodmart-child/js/motion.js` and use
  `get_stylesheet_directory_uri() . '/js/motion.js'` as the URL.

**How it gets there:**
- With Claude in Chrome (see SKILL.md): show the user the code and the target file, get a clear yes,
  copy the current `functions.php` content into the session log as a backup, then append the snippet
  in Appearance → Theme File Editor → **WoodMart Child** → `functions.php` → Update File. Reload the
  front end and check `typeof window.Motion === 'object'` in the console, and that wp-admin still loads.
  If the editor is disabled (`DISALLOW_FILE_EDIT`) or the save fails, stop and use the handoff below.
- Otherwise hand it over in the `references/php-overrides.md` format (SFTP / host file manager).
- Skip it if the snippet (`wmb_enqueue_motion`) is already in the file.

## 2. Rules for the animations

- Light: fades, small translates (≤ 40px), scale ≤ 1.05, durations 0.4–0.8s, stagger ≤ 0.1s.
- Animate only `opacity` and `transform` (no layout properties).
- Respect `prefers-reduced-motion`: do nothing (content stays visible) when it's set.
- Content must be visible without JS: never hide content in CSS; the script sets the initial state.
- Prefer WoodMart's built-in animations ("Animation" / "CSS animation" element options) when they
  match the design. Use Motion only for what those can't do.
- Target elements with an **Extra class name** in the element options: `m-fade-up`, `m-fade-in`,
  `m-stagger` (its children animate in sequence).

## 3. Theme Settings → Custom JS

Read the existing Custom JS first and append this block (never overwrite).

```js
/* == Global | Motion animations (window.Motion, enqueued in woodmart-child/functions.php) == */
(function () {
  function run() {
    var M = window.Motion;
    if (!M || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!document.querySelector('.m-fade-up, .m-fade-in, .m-stagger')) return;
    var animate = M.animate, inView = M.inView, stagger = M.stagger;

    document.querySelectorAll('.m-fade-up').forEach(function (el) {
      el.style.opacity = 0;
      inView(el, function () {
        animate(el, { opacity: [0, 1], transform: ['translateY(24px)', 'none'] },
          { duration: 0.6, ease: 'easeOut' });
      }, { amount: 0.2 });
    });

    document.querySelectorAll('.m-fade-in').forEach(function (el) {
      el.style.opacity = 0;
      inView(el, function () { animate(el, { opacity: [0, 1] }, { duration: 0.6 }); }, { amount: 0.2 });
    });

    document.querySelectorAll('.m-stagger').forEach(function (group) {
      var items = group.children;
      Array.prototype.forEach.call(items, function (c) { c.style.opacity = 0; });
      inView(group, function () {
        animate(items, { opacity: [0, 1], transform: ['translateY(16px)', 'none'] },
          { duration: 0.5, delay: stagger(0.08) });
      }, { amount: 0.2 });
    });
  }
  // Works whether WoodMart prints Custom JS before or after the deferred Motion script.
  if (window.Motion) run();
  else if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
})();
```

If Motion fails to load (CDN blocked), `run()` returns before hiding anything, so content stays visible.

Notes:
- If the site's caching/optimization plugin delays or combines JS, test with it on and off; exclude
  `wmb-motion` from "delay JS" if animations start late.
- Document each class used (page/section) in the Phase 7 handoff.

## Testing

Check desktop and mobile, with OS "reduce motion" on (no animation, everything visible) and off, and
with the Motion URL blocked (content must stay visible).
