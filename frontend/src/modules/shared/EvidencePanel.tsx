import type { StudioContext } from "./useStudioController";
export default function EvidencePanel({
  project,
  setTab,
  setFile,
  dirty,
  setComponent,
  setFocusedRequirement,
}: Pick<
  StudioContext,
  | "project"
  | "setTab"
  | "name"
  | "files"
  | "file"
  | "setFile"
  | "dirty"
  | "component"
  | "setComponent"
  | "setFocusedRequirement"
>) {
  if (!project) return null;
  return (
    <>
      <div className="evidence-stats">
        <div className="panel">
          <strong>{project.traceability.length}</strong>
          <span>Linked requirements</span>
        </div>
        <div className="panel">
          <strong>
            {project.tests.filter((t) => t.status === "passed").length}
          </strong>
          <span>Checks passed</span>
        </div>
        <div className="panel">
          <strong>
            {
              (project.rag_components || project.spec?.rag_components || [])
                .length
            }
          </strong>
          <span>Catalog matches</span>
        </div>
        <div className="panel">
          <strong>
            {project.tests.filter((t) => t.status === "not_run").length}
          </strong>
          <span>Checks still to run</span>
        </div>
      </div>
      <section className="panel">
        <h2>From requirement to source.</h2>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Requirement</th>
                <th>Screen</th>
                <th>Source files</th>
                <th>Check</th>
              </tr>
            </thead>
            <tbody>
              {project.traceability.map((r) => (
                <tr key={r.requirement}>
                  <td>
                    <button
                      className="id-badge"
                      onClick={() => {
                        setFocusedRequirement(r.requirement);
                        setTab("Requirements");
                      }}
                    >
                      {r.requirement}
                    </button>
                  </td>
                  <td>{r.page}</td>
                  <td>
                    {r.files.map((path) => (
                      <button
                        key={path}
                        className="text-button"
                        onClick={() => {
                          if (dirty && !confirm("Discard unsaved file edits?"))
                            return;
                          setFile(path);
                          setTab("Code");
                        }}
                      >
                        {path}
                      </button>
                    ))}
                  </td>
                  <td>{r.test}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="panel">
        <h2>Validation, with context.</h2>
        <p className="subtle">
          Structural checks and compilation are automated. They do not establish
          model accuracy or replace testing the app on a phone.
        </p>
        {project.tests.map((t) => (
          <div className="test-row" key={t.id}>
            <span>{t.status === "passed" ? "✓" : "○"}</span>
            <div>
              <strong>{t.name}</strong>
              <small>
                {t.id} · {t.kind}
              </small>
            </div>
            <span className="pill">{t.status}</span>
          </div>
        ))}
      </section>
      <section className="panel">
        <h2>Component inventory</h2>
        <p className="subtle">
          ProductCard is used by the generated app. Other catalog components are
          exported starter templates.
        </p>
        <div className="component-grid">
          {project.components
            .filter((c) => c.file.endsWith(".jsx"))
            .map((c) => (
              <button
                key={c.id}
                onClick={() => {
                  setComponent(c.name);
                  setTab("Preview");
                }}
              >
                <span>◇</span>
                <strong>{c.name}</strong>
                <small>
                  {c.id} · {c.source}
                  {c.used ? " · in use" : ""}
                </small>
              </button>
            ))}
        </div>
      </section>
      {project.feedback.length > 0 && (
        <section className="panel">
          <h2>Feedback history</h2>
          {project.feedback.map((f) => (
            <p key={f.id}>
              {f.requirement_id} · {f.text}
            </p>
          ))}
        </section>
      )}
    </>
  );
}
