# Animations with Motion (vanilla)

Framer Motion is a **React** library and doesn't apply to a WoodMart/WPBakery page. Use its vanilla JS
version, **Motion** (https://motion.dev), loaded **once** via Theme Settings → Custom JS. No `<script>`
tags in page content.

## Rules

- Light: fades, small translates (≤ 40px), scale ≤ 1.05, durations 0.4–0.8s, stagger ≤ 0.1s.
- Animate only `opacity` and `transform` (no layout properties).
- Respect `prefers-reduced-motion`: do nothing (content stays visible) when it's set.
- Content must be visible without JS: never hide content in CSS; the script sets the initial state.
- Prefer WoodMart's built-in animations ("Animation" / "CSS animation" options on elements) when they
  match the design — no JS needed. Use Motion only for what those can't do.
- Target elements via an **Extra class name** set in the element options, e.g. `m-fade-up`,
  `m-stagger` (children animate in sequence).
- Pin the Motion version; don't use `@latest` in production.

## Theme Settings → Custom JS

Read the existing Custom JS first and append this block (do not overwrite). Replace `X.Y.Z` with a
current stable version of `motion` checked on npm at build time, and confirm it with the user.

```js
/* == Global | Motion animations (motion.dev) == */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!document.querySelector('.m-fade-up, .m-fade-in, .m-stagger')) return;

  import('https://cdn.jsdelivr.net/npm/motion@X.Y.Z/+esm').then(function (Motion) {
    var animate = Motion.animate, inView = Motion.inView, stagger = Motion.stagger;

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
  }).catch(function () {
    document.querySelectorAll('.m-fade-up, .m-fade-in, .m-stagger, .m-stagger > *')
      .forEach(function (el) { el.style.opacity = ''; });
  });
})();
```

Notes:
- If the Custom JS field wraps code in jQuery ready, the block still works (it's self-contained).
- If the site's caching/optimization plugin delays or combines JS, test with it on and off.
- Document each class used (which page/section) in the Phase 7 handoff.

## Testing

Check desktop and mobile, with OS "reduce motion" on (no animation, everything visible) and off, and with
a throttled network (content must not stay invisible if the CDN fails).
