import BrandLogo from "../components/BrandLogo";
import ScreenShowcaseSection from "../modules/live_review_panel/ScreenShowcaseSection";
import type { Project } from "../modules/shared/types";
import AuthModal from "../components/auth/AuthModal";
import "../styles/studio.css";
import "../styles/appearance.css";
import "../styles/workbench.css";
import "../styles/studio-refinements.css";
import { API, request, tabs } from "../modules/shared/studioApi";
import InputInterface from "../modules/input_interface/InputInterface";
import StageTracker from "../modules/progress_and_status_panel/StageTracker";
import SrsViewerAndEditor from "../modules/srs_viewer_and_editor/SrsViewerAndEditor";
import LiveReviewPanel from "../modules/live_review_panel/LiveReviewPanel";
import CodeExplorer from "../modules/code_explorer/CodeExplorer";
import EvidencePanel from "../modules/shared/EvidencePanel";
import DeployDashboard from "../modules/deploy_dashboard/DeployDashboard";
import LiveLogStream from "../modules/progress_and_status_panel/LiveLogStream";
import useStudioController from "../modules/shared/useStudioController";
export default function StudioPage() {
  const context = useStudioController();
  const {
    appearance,
    project,
    setProject,
    projects,
    tab,
    setTab,
    user,
    setUser,
    authOpen,
    setAuthOpen,
    refinePrompt,
    setRefinePrompt,
    screenConfigs,
    busy,
    error,
    setError,
    online,
    dirty,
    setDirty,
    notice,
    setNotice,
    reviewDirty,
    setReviewDirty,
    active,
    current,
    action,
    accept,
    handleUpdateScreenConfig,
    handleUpdateRequirementText,
    handleApproveAndBuild,
    handleRefineScreens,
    logout,
    design,
    saveReview,
  } = context;
  return (
    <div
      className="studio-shell"
      data-theme={appearance.resolved}
      data-motion={appearance.animated ? "on" : "off"}
    >
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        onAuthSuccess={(u, t) => {
          setUser(u);
          localStorage.setItem("jinie_user", JSON.stringify(u));
          localStorage.setItem("jinie_auth_token", t);
          setNotice("Welcome, " + u.full_name + "!");
        }}
        apiBase={API}
      />
      <aside className="studio-sidebar">
        <a className="studio-logo" href="/" aria-label="Jinie home">
          <BrandLogo />
        </a>
        <div className="sidebar-caption">YOUR CREATIVE WORKSPACE</div>
        <button
          className="new-project"
          onClick={() => {
            if ((dirty || reviewDirty) && !confirm("Discard unsaved edits?"))
              return;
            setProject(null);
            setTab("Prompt");
            setDirty(false);
            setReviewDirty(false);
            localStorage.removeItem("jinie_project_id");
          }}
        >
          ＋ New project
        </button>
        <nav>
          {tabs.map((t, i) => (
            <button
              aria-label={t}
              key={t}
              className={tab === t ? "selected" : ""}
              onClick={() => setTab(t)}
              disabled={!project && t !== "Prompt"}
            >
              <span className="nav-icon">
                {["◈", "≡", "▦", "▣", "⌘", "◇", "↗"][i]}
              </span>
              {t}
              {t === "Preview" && current && <span className="tiny-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-caption">RECENT PROJECTS</div>
        <div className="recent-list">
          {projects.slice(0, 5).map((p) => (
            <button
              key={p.id}
              onClick={() =>
                action(async () => {
                  if (
                    (dirty || reviewDirty) &&
                    !confirm("Discard unsaved edits?")
                  )
                    return;
                  accept(await request<Project>("/projects/" + p.id));
                  setTab("Requirements");
                  setDirty(false);
                })
              }
            >
              <span>◈</span>
              {p.name}
            </button>
          ))}
          {!projects.length && <small>Your next idea starts here.</small>}
        </div>
        <div className="sidebar-bottom">
          {user ? (
            <div className="sidebar-user-block">
              <div className="sidebar-user-info">
                <div className="avatar" title={user.email}>
                  {user.initials}
                </div>
                <div className="sidebar-user-text">
                  <strong>{user.full_name}</strong>
                  <small>{user.email}</small>
                </div>
                <button
                  className="sidebar-logout-btn"
                  onClick={logout}
                  title="Sign out"
                >
                  Logout
                </button>
              </div>
              <div style={{ fontSize: 9, color: "var(--soft)" }}>
                React Native · Local workspace
              </div>
            </div>
          ) : (
            <div className="sidebar-user-block">
              <button
                className="sidebar-auth-btn"
                onClick={() => setAuthOpen(true)}
              >
                <span>👤</span> Sign In / Register ↗
              </button>
              <div
                style={{
                  fontSize: 9,
                  color: "var(--soft)",
                  textAlign: "center",
                }}
              >
                Sign in to save your identity
              </div>
            </div>
          )}
        </div>
      </aside>
      <div className="studio-main">
        <header className="studio-topbar">
          <span>
            Workspace <b>/</b> {project?.name || "New creation"}
          </span>
          <div>
            {user ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "4px 10px",
                  background: "var(--raised)",
                  borderRadius: 16,
                  border: "1px solid var(--edge)",
                }}
              >
                <span
                  style={{ fontSize: 11, fontWeight: 600, color: "var(--fg)" }}
                >
                  👤 {user.full_name}
                </span>
                <button
                  className="sidebar-logout-btn"
                  onClick={logout}
                  style={{ fontSize: 9, padding: "2px 6px" }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                className="text-button"
                onClick={() => setAuthOpen(true)}
                style={{ fontWeight: 600, fontSize: 11 }}
              >
                👤 Sign In
              </button>
            )}
            <span className={"connection " + (online ? "connected" : "")}>
              ● {online ? "Engine connected" : "Engine offline"}
            </span>
            <div className="appearance-controls">
              <label className="theme-picker">
                <span aria-hidden="true">
                  {appearance.resolved === "dark" ? "☾" : "☀"}
                </span>
                <select
                  aria-label="Workspace theme"
                  value={appearance.theme}
                  onChange={(e) =>
                    appearance.setTheme(
                      e.target.value as "light" | "dark" | "system",
                    )
                  }
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </label>
              <button
                className="motion-toggle"
                aria-label="Ambient animation"
                aria-pressed={appearance.motion}
                onClick={() => appearance.setMotion(!appearance.motion)}
                title="Toggle ambient animation"
              >
                {appearance.motion ? "✧" : "◇"}
                <span>Motion</span>
              </button>
            </div>
          </div>
        </header>
        <main className="studio-body">
          {error && (
            <div role="alert" className="alert error">
              <strong>Something went wrong!</strong>
              <span>{error}</span>
              <button onClick={() => setError("")} aria-label="Dismiss error">
                ×
              </button>
            </div>
          )}
          {notice && (
            <div role="status" className="alert">
              <span>{notice}</span>
              <button onClick={() => setNotice("")}>×</button>
            </div>
          )}
          {tab === "Prompt" && <InputInterface {...context} />}
          {project && tab !== "Prompt" && (
            <>
              <div className="workspace-heading">
                <div>
                  <span className="eyebrow">
                    {project.name} / {tab.toUpperCase()}
                  </span>
                  <h1>
                    {
                      (
                        {
                          Requirements:
                            "Software Requirements Specification (SRS).",
                          Screens: "Shape your screens.",
                          Preview: "Meet your new experience.",
                          Code: "Every detail, in your hands.",
                          Evidence: "See how it all connects.",
                          Deploy: "Ready for the next step.",
                        } as Record<string, string>
                      )[tab]
                    }
                  </h1>
                </div>
                <span className={"status-pill " + project.status}>
                  {active ? "◌ " : current ? "● " : "◈ "}
                  {project.status}
                </span>
              </div>
              <StageTracker {...context} />
              {project.api_plan && tab === "Requirements" && (
                <section className="panel" style={{ marginBottom: 18 }}>
                  <span className="eyebrow">REQUIREMENTS PLAN</span>
                  <p style={{ marginTop: 10 }}>{project.api_plan.summary}</p>
                  <p className="subtle">
                    Review the requirements below. The plan and sample catalog
                    are dynamically generated and tailored to your brief by
                    Jinie Core Engine.
                  </p>
                  {project.api_plan.unsupported_features.map((feature, i) => (
                    <p key={"limit" + i}>
                      Needs additional implementation: {feature}
                    </p>
                  ))}
                  {project.api_plan.questions.map((q, i) => (
                    <p key={"q" + i}>Clarify: {q}</p>
                  ))}
                </section>
              )}
              {project.error && (
                <div className="alert error" role="alert">
                  {project.error}
                </div>
              )}
              {tab === "Screens" && (
                <ScreenShowcaseSection
                  key={project.id}
                  project={project}
                  screenConfigs={screenConfigs}
                  onUpdateScreenConfig={handleUpdateScreenConfig}
                  onUpdateRequirement={handleUpdateRequirementText}
                  onUpdateDesign={design}
                  onBuildApp={handleApproveAndBuild}
                  refinement={refinePrompt}
                  onRefinementChange={setRefinePrompt}
                  onRefine={handleRefineScreens}
                  onSave={() =>
                    action(async () => {
                      await saveReview();
                      setNotice("Screen changes saved.");
                    })
                  }
                  dirty={reviewDirty}
                  busy={busy}
                  active={active}
                />
              )}
              {tab === "Requirements" && <SrsViewerAndEditor {...context} />}

              {tab === "Preview" && <LiveReviewPanel {...context} />}
              {tab === "Code" && <CodeExplorer {...context} />}
              {tab === "Evidence" && <EvidencePanel {...context} />}
              {tab === "Deploy" && <DeployDashboard {...context} />}
              <LiveLogStream {...context} />
            </>
          )}
          <footer className="studio-footer">
            <span>
              <BrandLogo /> <small>Ideas deserve to become real.</small>
            </span>
            <small>
              React Native · Local-first workspace · Built with intention
            </small>
          </footer>
        </main>
      </div>
    </div>
  );
}
