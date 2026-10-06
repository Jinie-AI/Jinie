import { useEffect, useState } from "react";
type Document = {
  name: string;
  sections: { title: string; note: string; entries: string[] }[];
};
export default function SrsDocument({
  url,
  revision,
  dirty,
}: {
  url: string;
  revision: number;
  dirty: boolean;
}) {
  const [doc, setDoc] = useState<Document | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch(url, { signal: controller.signal })
      .then((r) => {
        if (!r.ok)
          throw new Error(
            "Could not load the SRS. Restart the backend and reload.",
          );
        return r.json();
      })
      .then((data) => {
        setDoc(data);
        setError("");
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => controller.abort();
  }, [url, revision]);
  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <h2>Complete SRS document</h2>
      <p>
        {dirty
          ? "Save your edits to update this document and its exports."
          : "The website, PDF and Markdown export use the same saved specification."}
      </p>
      {error ? (
        <p role="alert">{error}</p>
      ) : !doc ? (
        <p>Loading specification…</p>
      ) : (
        doc.sections.map((section) => (
          <details
            key={section.title}
            style={{ padding: "14px 0", borderBottom: "1px solid var(--line)" }}
          >
            <summary style={{ cursor: "pointer", fontWeight: 700 }}>
              {section.title}
            </summary>
            <p style={{ opacity: 0.75 }}>{section.note}</p>
            <ul style={{ paddingLeft: 22 }}>
              {section.entries.map((entry, i) => (
                <li
                  key={i}
                  style={{
                    whiteSpace: "pre-wrap",
                    overflowWrap: "anywhere",
                    marginBottom: 14,
                    lineHeight: 1.65,
                  }}
                >
                  {entry}
                </li>
              ))}
            </ul>
          </details>
        ))
      )}
    </section>
  );
}
