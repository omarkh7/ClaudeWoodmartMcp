<?php // remove this line when appending to an existing functions.php
/**
 * Motion (motion.dev) — vanilla-JS Framer Motion. Added by woodmart-builder.
 * Append to: wp-content/themes/woodmart-child/functions.php
 * Exposes window.Motion (animate, inView, scroll, stagger, ...) on the front end.
 * Animation code goes in WoodMart → Theme Settings → Custom JS (see references/animation.md).
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
