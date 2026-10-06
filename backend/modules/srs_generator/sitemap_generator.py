"""Describe selected screens and supported navigation between them."""


def generate_sitemap(requirements):
    pages = list(dict.fromkeys(r["page"] for r in requirements))
    sitemap = [f"Application -> {page} | {next((r.get('id', '') for r in requirements if r['page'] == page), '')}" for page in pages]
    for source, target, action in [("products", "detail", "Select product"), ("home", "detail", "Select product"), ("search", "detail", "Select result"), ("detail", "cart", "Add/view cart"), ("cart", "checkout", "Proceed to checkout"), ("checkout", "orders", "View local orders")]:
        if source in pages and target in pages:
            sitemap.append(f"{source} -> {target}: {action}")
    if pages:
        sitemap.append("Primary navigation -> " + " / ".join(pages))
    return sitemap
