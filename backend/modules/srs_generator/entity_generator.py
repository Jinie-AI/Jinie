"""Derive conceptual entities only from selected screens and custom fields."""


def generate_entities(requirements, screen_configs):
    pages = list(dict.fromkeys(item["page"] for item in requirements))
    entities = []
    if any(page in pages for page in ("home", "products", "detail", "search", "cart", "checkout")):
        entities.extend([
            "Product: id, name, price, category, description, image_url, badge, rating. Catalogue records come from generated configuration.",
            "Category: label derived from Product.category. One category groups many products.",
        ])
    if "cart" in pages:
        entities.append("CartItem: productId, quantity. Each item references one Product; the local cart contains many items.")
    if any(page in pages for page in ("checkout", "orders")):
        entities.append("Order: local order record, purchased items and total. An order contains product/quantity snapshots. This is a device-local demo record, not a server-confirmed payment.")
    if any(page in pages for page in ("profile", "checkout")):
        entities.append("Customer details: customer name and address in local application state. This does not represent authenticated user accounts.")
    if "settings" in pages:
        entities.append("Preferences: notification preference and local application settings.")
    for page in pages:
        if not page.startswith("custom_"):
            continue
        config = screen_configs.get(page, {})
        fields = [field["label"] for section in config.get("sections", []) for field in section.get("fields", [])]
        entities.append(
            f"{config.get('title') or page}: " + ", ".join(fields)
            + ". Read-only display fields; no remote record service is provisioned."
        )
    return entities or ["No structured domain entities are defined for the selected screens."]
