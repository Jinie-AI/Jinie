# Prompt-driven screen composition

Home and catalogue screens now use a saved, validated composition plan instead of only selecting one fixed page template. The API receives the brief, local model suggestions, and retrieved component descriptions. It chooses section order, hero treatment, card style, image ratio, density, corners, and collection layout. Reference names are checked against the retrieved results.

The renderer supports hero, search, categories, collection, spotlight and statement blocks. Both the Screens design preview and Preview design view consume the same saved screen configurations. The working generated app renders the same composition through PlannedCommerce with cart, filtering and navigation callbacks. The two rendering technologies are not guaranteed pixel-identical.

Manual title, subtitle and layout edits update the corresponding composition blocks. Refinement receives the current saved configurations. Local-only planning uses explicit domain-based fallbacks; it does not pretend to be an API-generated plan. Existing projects can retain their prior appearance until refined and accepted again.

Scrollbars are hidden inside design previews and newly built working app previews while scrolling remains enabled. Rebuild an older generated app to update its preview bundle.

## Verification and limits

Composition tests cover section-order preservation, reference grounding, different domain fallbacks, mandatory catalogue content, and invalid model output. The planner tests mock API responses and do not incur paid calls.

This is a constrained commerce layout grammar, not unrestricted app generation. Retrieved component metadata guides design choices; third-party source code is not automatically imported. Other screens retain established implementations. Store publication remains disabled. Authentication, payments, persistent orders, multi-user authorization and release-device testing still require production-specific work before a public launch.
