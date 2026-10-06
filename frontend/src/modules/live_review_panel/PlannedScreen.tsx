import { useState } from "react";
import type { HtmlScreenMockupProps } from "./HtmlScreenMockup";
import "./planned-screen.css";
export type Composition = {
  version: 1;
  rationale: string;
  hero_style: "image" | "split" | "typographic";
  card_style: "elevated" | "outlined" | "flat";
  image_ratio: "portrait" | "square" | "landscape";
  density: "airy" | "balanced" | "compact";
  corners: "sharp" | "soft" | "round";
  category_style?: "chips" | "tiles";
  blocks: {
    kind:
      | "hero"
      | "search"
      | "categories"
      | "collection"
      | "spotlight"
      | "statement";
    title: string;
    body: string;
    layout: "grid" | "cards" | "editorial" | "rail" | "mosaic";
    reference_component: string;
  }[];
};
type Props = {
  plan: Composition;
  products: NonNullable<HtmlScreenMockupProps["products"]>;
  title?: string;
  subtitle?: string;
  primary: string;
  primaryInk: string;
  surface: string;
  ink: string;
  muted: string;
  showHero: boolean;
  showSearch: boolean;
  showBadges: boolean;
  onSelect: (page: string) => void;
  onProductSelect?: (id: string) => void;
  pages: string[];
};
export default function PlannedScreen({
  plan,
  products,
  title,
  subtitle,
  primary,
  primaryInk,
  surface,
  ink,
  muted,
  showHero,
  showSearch,
  showBadges,
  onSelect,
  onProductSelect,
  pages,
}: Props) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const categories = [
    "All",
    ...new Set(products.map((p) => p.category).filter(Boolean)),
  ];
  const filtered = products.filter(
    (p) =>
      (category === "All" || category === p.category) &&
      [p.name, p.category, p.description]
        .join(" ")
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const featured = products[0];
  const radius =
    plan.corners === "sharp" ? 3 : plan.corners === "round" ? 24 : 14;
  const ratio =
    plan.image_ratio === "portrait"
      ? "3 / 4"
      : plan.image_ratio === "landscape"
        ? "16 / 9"
        : "1";
  const gap =
    plan.density === "airy" ? 22 : plan.density === "compact" ? 8 : 14;
  return (
    <div
      className={"planned-screen density-" + plan.density}
      style={
        {
          gap,
          color: ink,
          "--plan-radius": radius + "px",
          "--plan-surface": surface,
          "--plan-ink": ink,
          "--plan-muted": muted,
        } as React.CSSProperties
      }
    >
      {plan.blocks.map((block, index) => {
        const key = block.kind + "-" + index;
        if (block.kind === "hero")
          return showHero ? (
            <section
              key={key}
              className={"plan-hero " + plan.hero_style}
              style={{ background: primary, color: primaryInk }}
            >
              {plan.hero_style !== "typographic" && featured?.image_url && (
                <img src={featured.image_url} alt={featured.name} />
              )}
              <div className="plan-hero-copy">
                <span className="plan-eyebrow">
                  {block.body || subtitle || "Selected for you"}
                </span>
                <h2>{block.title || title || "Find your next favourite."}</h2>
                {pages.includes("products") && (
                  <button
                    style={{ background: primaryInk, color: primary }}
                    onClick={() => onSelect("products")}
                  >
                    Explore collection →
                  </button>
                )}
              </div>
            </section>
          ) : null;
        if (block.kind === "search")
          return showSearch ? (
            <input
              key={key}
              className="plan-search"
              aria-label="Search collection"
              placeholder={block.title || "Search the collection"}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          ) : null;
        if (block.kind === "categories")
          return (
            <div
              key={key}
              className={"plan-categories " + (plan.category_style || "chips")}
            >
              {categories.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategory(c || "All")}
                  style={{
                    background: category === c ? primary : surface,
                    color: category === c ? primaryInk : ink,
                  }}
                >
                  {c}
                </button>
              ))}
            </div>
          );
        if (block.kind === "statement")
          return (
            <section key={key} className="plan-statement">
              <h3>{block.title || "Thoughtfully selected."}</h3>
              {block.body && <p>{block.body}</p>}
            </section>
          );
        if (block.kind === "spotlight")
          return featured ? (
            <section key={key} className="plan-spotlight">
              {featured.image_url && (
                <img src={featured.image_url} alt={featured.name} />
              )}
              <div>
                <span className="plan-eyebrow">
                  {block.title || "In focus"}
                </span>
                <h3>{featured.name}</h3>
                <p>{block.body || featured.description}</p>
                {pages.includes("detail") && (
                  <button onClick={() => onSelect("detail")}>Discover →</button>
                )}
              </div>
            </section>
          ) : null;
        return (
          <section key={key}>
            <h3 className="plan-section-title">
              {block.title || "Explore the collection"}
            </h3>
            {block.body && <p>{block.body}</p>}
            <div
              className={"plan-products " + block.layout}
              style={{ gap: plan.density === "compact" ? 8 : 12 }}
            >
              {filtered.map((product) => (
                <article
                  key={product.id}
                  className={"plan-product " + plan.card_style}
                >
                  <button
                    className="plan-product-open"
                    onClick={() => {
                      onProductSelect?.(product.id);
                      if (pages.includes("detail")) onSelect("detail");
                    }}
                    aria-label={"View " + product.name}
                  >
                    <div
                      className="plan-product-photo"
                      style={{ aspectRatio: ratio }}
                    >
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          loading="lazy"
                        />
                      ) : (
                        <span>{product.icon || "✦"}</span>
                      )}
                      {showBadges && product.badge && (
                        <span
                          className="plan-badge"
                          style={{ background: primary, color: primaryInk }}
                        >
                          {product.badge}
                        </span>
                      )}
                    </div>
                    <div className="plan-product-copy">
                      <span className="plan-eyebrow">{product.category}</span>
                      <h4>{product.name}</h4>
                      <strong>Rs. {product.price.toLocaleString()}</strong>
                    </div>
                  </button>
                  {pages.includes("cart") && (
                    <button
                      type="button"
                      onClick={() => {
                        onProductSelect?.(product.id);
                        onSelect("cart");
                      }}
                      aria-label={"Add " + product.name + " to cart"}
                      style={{
                        background: primary,
                        color: primaryInk,
                        border: 0,
                        borderRadius: 10,
                        minHeight: 44,
                        margin: 10,
                        padding: "10px 14px",
                        fontWeight: 700,
                      }}
                    >
                      Add to cart
                    </button>
                  )}
                </article>
              ))}
            </div>
            {!filtered.length && <p>No products match your search.</p>}
          </section>
        );
      })}
    </div>
  );
}
