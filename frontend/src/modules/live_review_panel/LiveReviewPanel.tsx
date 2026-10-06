import PreviewDevice from "./PreviewDevice";
import DesignPreview from "./DesignPreview";
import { API, request } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
export default function LiveReviewPanel({
  appearance,
  project,
  setTab,
  screenConfigs,
  component,
  setComponent,
  showWorkingApp,
  device,
  setDevice,
  previewScreen,
  setPreviewScreen,
  active,
  current,
  endpoint,
  action,
  accept,
}: Pick<
  StudioContext,
  | "appearance"
  | "project"
  | "setTab"
  | "screenConfigs"
  | "prompt"
  | "name"
  | "file"
  | "component"
  | "setComponent"
  | "showWorkingApp"
  | "device"
  | "setDevice"
  | "previewScreen"
  | "setPreviewScreen"
  | "active"
  | "current"
  | "endpoint"
  | "action"
  | "accept"
  | "design"
>) {
  if (!project) return null;
  return (
    <>
      <div className="preview-toolbar">
        <button
          className="make-changes-btn"
          onClick={() => setTab("Screens")}
          title="Refine prompt or modify design tokens"
        >
          ✏️ Make Changes
        </button>
        <select
          aria-label="Preview component"
          value={component}
          onChange={(e) => {
            setComponent(e.target.value);
          }}
        >
          <option value="">Full app</option>
          {project.components
            .filter((c) => c.file.endsWith(".jsx"))
            .map((c) => (
              <option key={c.id} value={c.name}>
                {c.name}
              </option>
            ))}
        </select>
        {!component && project.spec.pages.length > 0 && (
          <select
            aria-label="Focus screen"
            value={previewScreen}
            onChange={(e) => setPreviewScreen(e.target.value)}
            style={{ fontSize: 11, borderRadius: 8 }}
          >
            <option value="">All screens (Default flow)</option>
            {project.spec.pages.map((p, i) => (
              <option key={p} value={p}>
                Screen {i + 1}:{" "}
                {p === "products"
                  ? "Catalog"
                  : p.charAt(0).toUpperCase() + p.slice(1)}
              </option>
            ))}
          </select>
        )}
        <div className="segmented">
          {["mobile", "tablet", "desktop"].map((d) => (
            <button
              key={d}
              className={device === d ? "chosen" : ""}
              onClick={() => setDevice(d)}
            >
              {d === "desktop"
                ? "🖥️ Desktop Web"
                : d === "tablet"
                  ? "Tablet"
                  : "📱 Mobile"}
            </button>
          ))}
        </div>
        <button
          className="secondary"
          onClick={() => setTab("Screens")}
          title="Return to screen customizer"
        >
          📱 Screens flow ({project.spec.pages.length})
        </button>
        {current && (
          <a
            className="primary"
            href={API + endpoint("/download")}
            title="Download complete native & web source"
          >
            Download project ↓
          </a>
        )}
        {["failed", "cancelled"].includes(project.status) && (
          <button
            className="primary"
            onClick={() =>
              action(async () =>
                accept(await request(endpoint("/build"), "POST")),
              )
            }
          >
            Retry build
          </button>
        )}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "8px 16px",
          background: "var(--surface, #ffffff)",
          borderRadius: 12,
          border: "1px solid var(--edge, #e2e5ec)",
          marginBottom: 14,
          fontSize: 11,
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "#16a34a", fontWeight: 700 }}>
            ✓ Approved screens active:
          </span>
          <span
            style={{
              color: "var(--ink, #20232b)",
              fontWeight: 600,
            }}
          >
            {project.spec.pages
              .map((p, i) => `${i + 1}. ${p === "products" ? "Catalog" : p}`)
              .join("  ·  ")}
          </span>
        </div>
        <div style={{ color: "var(--soft, #646b79)", fontSize: 10 }}>
          {device === "desktop"
            ? "Desktop · 1280px viewport"
            : device === "tablet"
              ? "Tablet · 820px viewport"
              : "Phone · 375px viewport"}{" "}
          · {showWorkingApp ? "Working generated app" : "Design preview"}
        </div>
      </div>
      {project.build_revision !== null ? (
        <>
          <div
            className="preview-stage"
            onPointerMove={appearance.move}
            onPointerLeave={appearance.reset}
          >
            {!showWorkingApp ? (
              <DesignPreview
                project={project}
                page={previewScreen || project.requirements[0]?.page || "home"}
                configs={screenConfigs}
                onSelect={setPreviewScreen}
                device={device}
              />
            ) : (
              <PreviewDevice device={device}>
                <div className="device-top">
                  <i />
                  <span>JINIE WORKING APP · {device.toUpperCase()}</span>
                  <i />
                </div>
                <iframe
                  title="Generated React Native app"
                  key={
                    project.id +
                    "-" +
                    project.build_revision +
                    "-" +
                    previewScreen
                  }
                  src={
                    API +
                    endpoint("/preview/index.html") +
                    "?v=" +
                    project.build_revision +
                    "&component=" +
                    encodeURIComponent(component) +
                    (previewScreen
                      ? "&page=" + encodeURIComponent(previewScreen)
                      : "")
                  }
                  sandbox="allow-scripts"
                  style={{
                    height:
                      device === "tablet"
                        ? 1024
                        : device === "desktop"
                          ? 800
                          : 640,
                  }}
                />
              </PreviewDevice>
            )}
          </div>
          {!current && (
            <p className="subtle">
              The working app uses the last successful build. Accept screens
              again to rebuild your changes.
            </p>
          )}
        </>
      ) : (
        <div className="empty-stage">
          <div className={"small-orb " + (active ? "spinning" : "")}>✦</div>
          <h2>
            {active
              ? "Your idea is taking shape."
              : "Your preview starts with a build."}
          </h2>
          <p>
            Approve the brief and generate your app to explore the real output.
          </p>
        </div>
      )}
    </>
  );
}
