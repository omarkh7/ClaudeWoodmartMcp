# Contact Form 7 forms

All forms use **Contact Form 7** (CF7). No custom HTML forms, no other form plugins unless the user asks.

## Workflow

1. List the fields from the design (label, type, required, placeholder, options).
2. Write the CF7 **Form** tab markup and the **Mail** tab settings (below) and show them.
3. If an MCP ability can create CF7 forms (`wpcf7_contact_form` post type), create it and read it back.
   Otherwise give the markup to the user: Contact → Add New → paste Form tab → set Mail tab → Save.
4. **Ask for the form ID / shortcode** (`[contact-form-7 id="abc1234" title="Contact"]`). Never guess it.
5. Place it with the WoodMart/WPBakery **Contact Form 7** element (or the `contact-form-7` shortcode /
   CF7 block on block sites).
6. Style via WoodMart form settings (Theme Settings → Styles and colors → form style) first; only then
   minimal CSS in Theme Settings → Custom CSS, scoped with a class like `.wd-form-contact`.

## Markup patterns

Use CF7 tags; wrap with simple classes so it lays out without much CSS.

```text
<div class="cf7-row cf7-row--2">
  <p>[text* your-name autocomplete:name placeholder "Full name"]</p>
  <p>[email* your-email autocomplete:email placeholder "Email"]</p>
</div>
<p>[tel your-phone autocomplete:tel placeholder "Phone"]</p>
<p>[select your-subject include_blank "General" "Sales" "Support"]</p>
<p>[textarea* your-message x4 placeholder "Message"]</p>
<p>[acceptance accept-terms] I agree to the <a href="/privacy-policy/">privacy policy</a>. [/acceptance]</p>
<p>[submit class:btn class:btn-color-primary "Send message"]</p>
```

Newsletter (single line):

```text
<div class="cf7-inline">[email* your-email placeholder "Your email"][submit "Subscribe"]</div>
```

Labels: if the design shows visible labels, use `<label> Name [text* your-name] </label>`; if not, keep
placeholders and add accessible labels.

## Mail tab (show the user, they fill the real addresses)

- To: `[_site_admin_email]` (or the address the user gives)
- From: `[_site_title] <wordpress@DOMAIN>` — must be the site's domain for deliverability
- Subject: `[_site_title] — "[your-subject]"`
- Additional headers: `Reply-To: [your-email]`
- Body: list every field tag.

## Spam / security

- Recommend CF7's built-in Cloudflare Turnstile or reCAPTCHA integration (Contact → Integration). The
  keys are entered there by the user — never put them in Custom JS or page content.
- Recommend an SMTP plugin for reliable delivery; credentials stay in that plugin's settings/`wp-config.php`.
