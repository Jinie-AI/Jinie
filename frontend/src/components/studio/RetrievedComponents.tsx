import { useState } from "react";

export interface RetrievedComponent {
  name: string;
  category?: string;
  description?: string;
  score?: number;
  props?: string[];
  screens?: string[];
}

interface Props {
  components: RetrievedComponent[];
}

export default function RetrievedComponents({ components }: Props) {
  const [expanded, setExpanded] = useState(false);
  const unique = [
    ...new Map(components.map((item) => [item.name, item])).values(),
  ];
  const visible = expanded ? unique : unique.slice(0, 6);

  return (
    <section className="panel library-panel" aria-labelledby="library-title">
      <div className="panel-title">
        <div>
          <span className="eyebrow">COMPONENT LIBRARY</span>
          <h2 id="library-title">A foundation for your screens.</h2>
        </div>
        <span className="pill">{unique.length} matches</span>
      </div>
      <p className="subtle library-intro">
        Catalog references selected for your brief. These guide screen planning;
        the source inventory below shows the components included in your build.
      </p>
      {unique.length === 0 ? (
        <p className="library-empty">
          No relevant catalog matches for this brief. Standard screen components
          remain available.
        </p>
      ) : (
        <div className="library-grid">
          {visible.map((item) => (
            <article className="library-card" key={item.name}>
              <div className="library-card-heading">
                <span className="library-symbol" aria-hidden="true">
                  ◇
                </span>
                <div>
                  <h3>{item.name.replace(/([a-z])([A-Z])/g, "$1 $2")}</h3>
                  <span className="library-category">
                    {item.category || "Interface"}
                  </span>
                </div>
              </div>
              <p>
                {item.description ||
                  "A reusable interface pattern from the component catalog."}
              </p>
              <div className="library-screens">
                {item.screens?.length ? (
                  item.screens.map((screen) => (
                    <span key={screen}>
                      {screen === "products" ? "Catalog" : screen}
                    </span>
                  ))
                ) : (
                  <span>Brief reference</span>
                )}
              </div>
              <details className="library-details">
                <summary>Reference details</summary>
                <p>Catalog name: {item.name}</p>
                {typeof item.score === "number" && (
                  <p>
                    Retrieval similarity: {item.score.toFixed(3)} · not an
                    accuracy score
                  </p>
                )}
                {!!item.props?.length && (
                  <p>Properties: {item.props.join(", ")}</p>
                )}
              </details>
            </article>
          ))}
        </div>
      )}
      {unique.length > 6 && (
        <button
          className="text-button library-more"
          aria-expanded={expanded}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded
            ? "Show fewer components"
            : `View all ${unique.length} components`}
        </button>
      )}
    </section>
  );
}
