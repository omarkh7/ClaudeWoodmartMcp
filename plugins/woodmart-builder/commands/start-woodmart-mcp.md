---
description: Start the WoodMart builder - shows the steps, then asks you one question at a time
argument-hint: "[optional: site domain or what you want to build]"
---

Start the **woodmart-builder** workflow now.

1. Load the `woodmart-builder` skill (Skill tool) and follow its `SKILL.md` exactly: its global
   rules, its gated phases and its reference files.

2. Before asking anything, show the user this overview, short, as a numbered list:

   **WoodMart builder - the steps**
   1. Connect the site (MCP)
   2. Design source (Figma or screenshots)
   3. Project questions (info site or shop, Framer Motion animations, blog, page list)
   4. Global settings (fonts, colors, buttons, header/footer) - before → after, applied only after you approve
   5. Build pages (WPBakery + WoodMart elements, Figma spacing in the Design tab, all as Draft)
   6. WooCommerce layouts (shops only, kept inactive)
   7. Review & handoff

   Then add one line: "I'll ask one step at a time and wait for your answer. Nothing is published
   without your OK."

3. Start **Phase 1**. Check which `woodmart-*` MCP servers are already connected in this session.
   - If one or more are connected, list them and ask: use one of these sites, or connect a new site?
   - If none are connected, ask for the new site's MCP config, as Phase 1 describes.

4. Ask only that first question, then **stop and wait** for the answer. Never answer for the user and
   never move to the next phase until its gate is met.

Extra context from the user (may be empty): $ARGUMENTS
