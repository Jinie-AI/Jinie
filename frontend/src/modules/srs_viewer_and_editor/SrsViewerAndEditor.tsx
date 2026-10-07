import { assetUrl } from "../shared/studioApi";
import SrsDocument from "./SrsDocument";
import { API, pages } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
// Module 13 - SRS Review: lets users edit, select and approve requirements before accepting the screen design.
export default function SrsViewerAndEditor({
  project,
  setProject,
  setTab,
  busy,
  setNotice,
  reviewDirty,
  setReviewDirty,
  active,
  endpoint,
  action,
  updateRequirement,
  saveReview,
}: Pick<
  StudioContext,
  | "project"
  | "setProject"
  | "setTab"
  | "name"
  | "busy"
  | "dirty"
  | "component"
  | "setNotice"
  | "reviewDirty"
  | "setReviewDirty"
  | "active"
  | "endpoint"
  | "action"
  | "updateRequirement"
  | "saveReview"
>) {
  if (!project) return null;
  return (
    <div className="srs-full-panel">
      <section className="panel">
        <div
          className="panel-title"
          style={{
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div>
            <span className="eyebrow" style={{ letterSpacing: 1.5 }}>
              ✦ SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
            </span>
            <h2 style={{ fontSize: 25, margin: "6px 0 4px" }}>
              Functional & Non-Functional Specifications
            </h2>
            <p className="subtle" style={{ margin: 0 }}>
              Review the screen requirements and quality targets before
              building.
            </p>
          </div>
          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <a
              href={assetUrl(API + endpoint("/srs.pdf"))}
              target="_blank"
              rel="noreferrer"
              download={`SRS_${project.name}.pdf`}
              className="primary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "10px 18px",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              <span>📄</span> Export SRS PDF ↓
            </a>
          </div>
        </div>

        <div
          className="detected-category-card"
          style={{
            padding: "14px 18px",
            borderRadius: 14,
            background: "rgba(124, 92, 224, 0.1)",
            border: "1px solid rgba(124, 92, 224, 0.25)",
            marginBottom: 22,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 10,
          }}
        >
          <div>
            <strong
              style={{
                fontSize: 15,
                textTransform: "capitalize",
                color: "var(--fg)",
              }}
            >
              Detected Business Domain:{" "}
              {project.spec.business_label || project.spec.business}
            </strong>
            <p className="subtle" style={{ margin: "3px 0 0", fontSize: 11 }}>
              Screen plan prepared from your brief and component library
            </p>
          </div>
          <div
            style={{
              display: "flex",
              gap: 8,
              alignItems: "center",
            }}
          >
            <span
              className="pill"
              style={{
                textTransform: "capitalize",
                fontSize: 11,
                background: "rgba(124, 92, 224, 0.2)",
              }}
            >
              Category: {project.spec.business}
            </span>
            <span
              className="pill"
              style={{
                fontSize: 11,
                background: "rgba(22, 163, 74, 0.15)",
                color: "#16a34a",
                borderColor: "rgba(22, 163, 74, 0.3)",
              }}
            >
              Editable specification
            </span>
          </div>
        </div>

        {/* Section 1: Functional Requirements */}
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 12,
            }}
          >
            <div>
              <h3
                style={{
                  fontSize: 16,
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span style={{ color: "var(--purple)" }}>1.</span> Functional
                Requirements (FR)
              </h3>
              <p className="subtle" style={{ margin: "2px 0 0", fontSize: 11 }}>
                Features and interactive actions provided by each mobile screen.
                You can edit requirements or add/remove screens freely.
              </p>
            </div>
            <span className="pill">
              {project.requirements.length} Active Screens
            </span>
          </div>

          <div className="requirements-list" style={{ marginTop: 8 }}>
            {project.requirements.map((r, i) => (
              <div
                className="requirement"
                key={r.id}
                id={"requirement-" + r.id}
                style={{
                  padding: "14px 16px",
                  background: "var(--canvas, #f7f8fa)",
                  border: "1px solid var(--edge, #e2e5ec)",
                  borderRadius: 14,
                  marginBottom: 12,
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                <div>
                  <div
                    className="requirement-label"
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                    }}
                  >
                    <span className="id-badge" style={{ fontWeight: 700 }}>
                      {r.id}
                    </span>
                    <strong
                      style={{
                        fontSize: 13,
                        textTransform: "capitalize",
                      }}
                    >
                      {r.page === "products"
                        ? "Catalog / Menu"
                        : r.page
                            .replace(/^custom_/, "")
                            .replaceAll("_", " ")}{" "}
                      Screen
                    </strong>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        color: "#15803d",
                        background: "rgba(22, 163, 74, 0.12)",
                        padding: "2px 8px",
                        borderRadius: 10,
                      }}
                    >
                      Included in plan
                    </span>
                    <button
                      className="remove"
                      aria-label={"Remove " + r.page}
                      disabled={active || project.requirements.length === 1}
                      onClick={() => {
                        const nextPages = project.spec.pages.filter(
                          (p) => p !== r.page,
                        );
                        setProject({
                          ...project,
                          requirements: project.requirements.filter(
                            (_, j) => j !== i,
                          ),
                          spec: {
                            ...project.spec,
                            pages: nextPages,
                          },
                        });
                        setReviewDirty(true);
                      }}
                      style={{ marginLeft: "auto", fontSize: 16 }}
                    >
                      ×
                    </button>
                  </div>
                  <textarea
                    aria-label={r.page + " requirement"}
                    rows={2}
                    value={r.text}
                    disabled={active}
                    onChange={(e) =>
                      updateRequirement(i, { text: e.target.value })
                    }
                    style={{
                      width: "100%",
                      marginTop: 8,
                      background: "var(--surface, #ffffff)",
                      border: "1px solid var(--edge, #e2e5ec)",
                      borderRadius: 10,
                      padding: "8px 10px",
                      fontSize: 12,
                      lineHeight: 1.5,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="page-add" style={{ marginTop: 12 }}>
            <small
              style={{
                display: "inline-block",
                marginRight: 8,
                fontSize: 11,
                color: "var(--soft)",
              }}
            >
              ADD OPTIONAL SCREEN:
            </small>
            {pages
              .filter((p) => !project.requirements.some((r) => r.page === p))
              .map((p) => (
                <button
                  disabled={active}
                  key={p}
                  onClick={() => {
                    const id =
                      "REQ-" +
                      String(
                        Math.max(
                          ...project.requirements.map((r) =>
                            Number(r.id.slice(4)),
                          ),
                        ) + 1,
                      ).padStart(3, "0");
                    setProject({
                      ...project,
                      requirements: [
                        ...project.requirements,
                        {
                          id,
                          page: p,
                          text:
                            "Provide the " +
                            p +
                            " screen using the supported commerce workflow.",
                          approved: true,
                        },
                      ],
                      spec: {
                        ...project.spec,
                        pages: [...project.spec.pages, p],
                      },
                    });
                    setReviewDirty(true);
                  }}
                >
                  ＋ {p}
                </button>
              ))}
          </div>
        </div>

        {/* Section 2: Non-Functional Requirements */}
        <div
          style={{
            marginBottom: 24,
            borderTop: "1px solid var(--line)",
            paddingTop: 20,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 12,
            }}
          >
            <div>
              <h3
                style={{
                  fontSize: 16,
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span style={{ color: "var(--purple)" }}>2.</span>{" "}
                Non-Functional Requirements (NFR)
              </h3>
              <p className="subtle" style={{ margin: "2px 0 0", fontSize: 11 }}>
                Performance, accessibility and persistence targets to validate
                in the working app.
              </p>
            </div>
            <span className="pill">
              {project.nfr?.length || 5} Quality targets
            </span>
          </div>

          <div className="nfr-grid">
            {(project.nfr || []).map((n) => (
              <div className="nfr-card" key={n.id}>
                <div className="nfr-card-header">
                  <span className="id-badge">{n.id}</span>
                  <span
                    className="pill"
                    style={{
                      fontSize: 9,
                      background: "rgba(124, 92, 224, 0.1)",
                    }}
                  >
                    {n.category || "Quality"}
                  </span>
                </div>
                <p>{n.text}</p>
              </div>
            ))}
          </div>
        </div>

        <SrsDocument
          url={API + endpoint("/srs.json")}
          revision={project.revision}
          dirty={reviewDirty}
        />
        {/* Bottom Actions */}
        <div
          className="panel-actions"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            marginTop: 26,
            paddingTop: 20,
            borderTop: "1px solid var(--line)",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <button
              className="secondary"
              disabled={busy || active || !reviewDirty}
              onClick={() =>
                action(async () => {
                  await saveReview();
                  setNotice("Requirements changes saved.");
                })
              }
            >
              Save edits
            </button>
            <button className="secondary" onClick={() => setTab("Screens")}>
              Screens customizer →
            </button>
            <a
              href={assetUrl(API + endpoint("/srs.pdf"))}
              target="_blank"
              rel="noreferrer"
              download={`SRS_${project.name}.pdf`}
              className="secondary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span>📄</span> Download SRS PDF
            </a>
          </div>

          <button
            className="primary"
            disabled={busy || active}
            style={{
              fontSize: 13,
              padding: "13px 24px",
              boxShadow: "0 6px 20px rgba(124,92,224,0.35)",
            }}
            onClick={() =>
              action(async () => {
                await saveReview(true);
                setTab("Screens");
              })
            }
          >
            Accept requirements & review screens ↗
          </button>
        </div>
      </section>
    </div>
  );
}
