import BrandLogo from "../components/BrandLogo";
import SrsDocument from "../components/studio/SrsDocument";
import { useEffect, useRef, useState } from "react";
import "../styles/studio.css";
import "../styles/appearance.css";
import "../styles/workbench.css";
import { useStudioAppearance } from "../hooks/useStudioAppearance";
import PreviewDevice from "../components/preview/PreviewDevice";
import ScreenShowcaseSection from "../components/preview/ScreenShowcaseSection";
import RetrievedComponents from "../components/studio/RetrievedComponents";
import type {
  Requirement,
  Design,
  Project,
  Summary,
} from "../components/studio/types";
import PromptHero from "../components/studio/PromptHero";
import DesignPreview from "../components/preview/DesignPreview";
import FileTree from "../components/studio/FileTree";
import "../styles/studio-refinements.css";
import AuthModal, { type User } from "../components/auth/AuthModal";
import type { ScreenConfigData } from "../components/preview/HtmlScreenMockup";
import EditorModule from "react-simple-code-editor";
const Editor =
  (EditorModule as unknown as { default?: typeof EditorModule }).default ??
  EditorModule;
import Prism from "prismjs";
import "prismjs/components/prism-jsx";
import "prismjs/components/prism-json";
import "prismjs/themes/prism.css";
const API =
  (
    import.meta.env.VITE_API_URL ||
    (typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
      ? ""
      : "http://127.0.0.1:8000")
  ).replace(/\/$/, "") + "/api";
async function request<T>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), method === "GET" ? 20000 : 120000);
  try {
  const response = await fetch(API + path, {
    signal: controller.signal,
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
  });
  if (!response.ok) {
    let message: string;
    try {
      const body = await response.json();
      message =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail);
    } catch {
      message = response.statusText;
    }
    throw new Error(message);
  }
  return await response.json();
  } catch (error) {
    if (controller.signal.aborted) throw new Error("The server took too long to respond. Check recent projects before trying again; the server may still finish saving your request.");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}
const samples = [
  {
    name: "The Everyday Edit",
    text: "Build a minimal clothing boutique with home, products, product detail, cart, checkout, search, about and contact pages.",
  },
  {
    name: "Crave Kitchen",
    text: "Mujhe food restaurant ki app chahiye. Menu products, cart, checkout cash on delivery, search aur contact page ho. Playful design.",
  },
  {
    name: "Forma Living",
    text: "Create a luxury furniture shop with a home page, catalog, product details, cart, checkout and contact.",
  },
];
const pages = [
  "home",
  "products",
  "detail",
  "cart",
  "checkout",
  "contact",
  "about",
  "search",
  "settings",
  "profile",
];
const tabs = [
  "Prompt",
  "Requirements",
  "Screens",
  "Preview",
  "Code",
  "Evidence",
  "Deploy",
];
export default function StudioPage() {
  const appearance = useStudioAppearance();
  const [project, setProject] = useState<Project | null>(null),
    [projects, setProjects] = useState<Summary[]>([]),
    [tab, setTab] = useState("Prompt");
  const [user, setUser] = useState<User | null>(() => {
      try {
        const saved = localStorage.getItem("jinie_user");
        return saved && localStorage.getItem("jinie_auth_token")
          ? (JSON.parse(saved) as User)
          : null;
      } catch {
        return null;
      }
    }),
    [authOpen, setAuthOpen] = useState(false);
  const [refinePrompt, setRefinePrompt] = useState("");
  const [screenConfigs, setScreenConfigs] = useState<
    Record<string, ScreenConfigData>
  >({});
  const [prompt, setPrompt] = useState(samples[0].text),
    [name, setName] = useState(samples[0].name),
    [reference, setReference] = useState(""),
    [referenceName, setReferenceName] = useState("");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [online, setOnline] = useState(false);
  const [files, setFiles] = useState<string[]>([]),
    [file, setFile] = useState("App.jsx"),
    [code, setCode] = useState(""),
    [dirty, setDirty] = useState(false);
  const [component, setComponent] = useState("");
  const [focusedRequirement, setFocusedRequirement] = useState("");
  useEffect(() => {
    if (tab === "Requirements" && focusedRequirement) {
      document
        .getElementById("requirement-" + focusedRequirement)
        ?.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }, [tab, focusedRequirement]);
  const showWorkingApp = Boolean(component);
  const [device, setDevice] = useState("mobile"),
    [previewScreen, setPreviewScreen] = useState("");
  const [notice, setNotice] = useState(""),
    [reviewDirty, setReviewDirty] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const actionRunning = useRef(false);
  const active =
    project?.status === "building" || project?.status === "deploying";
  const current =
    project?.status === "ready" && project.build_revision === project.revision;
  const endpoint = (suffix = "") => "/projects/" + project!.id + suffix;
  async function action(fn: () => Promise<void>) {
    if (actionRunning.current) return;
    actionRunning.current = true;
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not complete the request.",
      );
    } finally {
      actionRunning.current = false;
      setBusy(false);
    }
  }
  function accept(p: Project) {
    setProject(p);
    try { localStorage.setItem("jinie_project_id", p.id); } catch { /* Project is still available in this session. */ }
    const cfgs = (p.screen_configs ||
      (p.spec && p.spec.screen_configs) ||
      {}) as Record<string, ScreenConfigData>;
    setScreenConfigs(cfgs);
    setReviewDirty(false);
  }
  function mergeScreenConfig(
    current: ScreenConfigData,
    change: Partial<ScreenConfigData>,
  ): ScreenConfigData {
    const next = { ...current, ...change };
    if (next.composition && !change.composition) {
      next.composition = {
        ...next.composition,
        blocks: next.composition.blocks.map((block) => ({
          ...block,
          ...(block.kind === "hero" && change.title !== undefined
            ? { title: change.title }
            : {}),
          ...(block.kind === "hero" && change.subtitle !== undefined
            ? { body: change.subtitle }
            : {}),
          ...(block.kind === "collection" && change.layout
            ? { layout: change.layout }
            : {}),
        })),
      };
    }
    return next;
  }
  function handleUpdateScreenConfig(
    page: string,
    configChange: Partial<ScreenConfigData>,
  ) {
    setScreenConfigs((prev) => ({
      ...prev,
      [page]: mergeScreenConfig(prev[page] || {}, configChange),
    }));
    setReviewDirty(true);
  }
  function handleUpdateRequirementText(page: string, text: string) {
    if (!project) return;
    setProject({
      ...project,
      requirements: project.requirements.map((r) =>
        r.page === page ? { ...r, text } : r,
      ),
    });
    setReviewDirty(true);
  }
  async function applyScreenRefinement() {
    await saveReview(true);
    if (refinePrompt.trim()) {
      const updated = await request<Project>(
        endpoint("/refine-design"),
        "POST",
        { instructions: refinePrompt.trim() },
      );
      accept(updated);
      setRefinePrompt("");
    }
  }
  async function handleApproveAndBuild() {
    await action(async () => {
      await applyScreenRefinement();
      accept(await request<Project>(endpoint("/build"), "POST"));
      setComponent("");
      setPreviewScreen("");
      setTab("Preview");
    });
  }
  async function handleRefineScreens() {
    await action(async () => {
      await applyScreenRefinement();
      setNotice(
        "Your screens have been updated. Review them, then accept to build.",
      );
    });
  }
  useEffect(() => {
    let alive = true;
    try {
      const u = localStorage.getItem("jinie_user");
      const t = localStorage.getItem("jinie_auth_token");
      if (u && t) {
        fetch(API + "/auth/me", { headers: { Authorization: "Bearer " + t } })
          .then((r) => r.json())
          .then((d) => {
            if (alive && d.user) setUser(d.user);
          })
          .catch(() => {});
      }
    } catch {
      /* Storage may be unavailable in private browsing. */
    }
    request<{
      models: Record<string, string>;
      engine?: { configured: boolean };
    }>("/health")
      .then(() => {
        if (alive) {
          setOnline(true);
        }
      })
      .catch(() => {
        if (alive)
          setError(
            "Backend is offline. Start it using the commands in START_HERE.md, then refresh.",
          );
      });
    request<Summary[]>("/projects")
      .then((p) => {
        if (alive) setProjects(p);
      })
      .catch(() => {});
    const id = localStorage.getItem("jinie_project_id");
    if (id)
      request<Project>("/projects/" + id)
        .then((p) => {
          if (alive) accept(p);
        })
        .catch(() => localStorage.removeItem("jinie_project_id"));
    return () => {
      alive = false;
    };
  }, []);
  function logout() {
    const t = localStorage.getItem("jinie_auth_token");
    if (t)
      fetch(API + "/auth/logout", {
        method: "POST",
        headers: { Authorization: "Bearer " + t },
      }).catch(() => {});
    localStorage.removeItem("jinie_user");
    localStorage.removeItem("jinie_auth_token");
    setUser(null);
    setNotice("Signed out successfully.");
  }
  useEffect(() => {
    if (!project?.id || !active) return;
    const id = project.id;
    let alive = true;
    const timer = setInterval(() => {
      request<Project>("/projects/" + id)
        .then((p) => {
          if (alive) setProject(p);
        })
        .catch((e) => {
          if (alive) setError(e.message);
        });
    }, 650);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [project?.id, active]);
  useEffect(() => {
    if (!project?.id || tab !== "Code") return;
    let alive = true;
    request<string[]>("/projects/" + project.id + "/files")
      .then((f) => {
        if (alive) {
          setFiles(f);
          setFile((current) =>
            f.length > 0 && !f.includes(current) ? f[0] : current,
          );
        }
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [project?.id, project?.build_revision, project?.revision, tab]);
  useEffect(() => {
    if (!project?.id || tab !== "Code" || !files.includes(file)) return;
    let alive = true;
    request<{ content: string }>(
      "/projects/" + project.id + "/file?path=" + encodeURIComponent(file),
    )
      .then((f) => {
        if (alive) {
          setCode(f.content);
          setDirty(false);
        }
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [
    project?.id,
    file,
    files,
    tab,
    project?.build_revision,
    project?.revision,
  ]);
  function updateRequirement(index: number, change: Partial<Requirement>) {
    if (!project) return;
    setProject({
      ...project,
      requirements: project.requirements.map((r, i) =>
        i === index ? { ...r, ...change } : r,
      ),
    });
    setReviewDirty(true);
  }
  function design(change: Partial<Design>) {
    if (project) {
      if (change.layout) {
        setScreenConfigs((prev) =>
          Object.fromEntries(
            Object.entries(prev).map(([page, config]) => [
              page,
              mergeScreenConfig(config, {
                layout: change.layout as ScreenConfigData["layout"],
              }),
            ]),
          ),
        );
      }
      setProject({ ...project, design: { ...project.design, ...change } });
      setReviewDirty(true);
    }
  }
  async function saveReview(approveRequirements = false) {
    const p = await request<Project>(endpoint("/review"), "PUT", {
      requirements: project!.requirements.map((item) =>
        approveRequirements ? { ...item, approved: true } : item,
      ),
      design: project!.design,
      business: project!.spec.business,
      screen_configs: screenConfigs,
    });
    accept(p);
    return p;
  }
  function dictate() {
    type Recognition = {
      lang: string;
      continuous: boolean;
      interimResults: boolean;
      start: () => void;
      onresult: ((e: { results: { transcript: string }[][] }) => void) | null;
      onerror: ((e: { error: string }) => void) | null;
    };
    const host = window as unknown as {
      SpeechRecognition?: new () => Recognition;
      webkitSpeechRecognition?: new () => Recognition;
    };
    const Speech = host.SpeechRecognition || host.webkitSpeechRecognition;
    if (!Speech) {
      setError(
        "Speech input is unavailable in this browser. Type or paste your brief.",
      );
      return;
    }
    const recognition = new Speech();
    recognition.lang = "en-PK";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (e) =>
      setPrompt((p) => p + " " + e.results[0][0].transcript);
    recognition.onerror = (e) => setError("Speech input: " + e.error);
    recognition.start();
    setNotice(
      "Listening for your brief. Your browser may use its speech service.",
    );
  }
  async function upload(f: File) {
    await action(async () => {
      const data = new FormData();
      data.append("file", f);
      const r = await fetch(API + "/references", {
        method: "POST",
        body: data,
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail);
      setReference(body.text);
      setReferenceName(body.name);
    });
  }
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
              <strong>Something needs attention</strong>
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
          {tab === "Prompt" && (
            <>
              <PromptHero
                onPointerMove={appearance.move}
                onPointerLeave={appearance.reset}
              />
              <div className="create-grid prompt-layout">
                <section className="panel prompt-panel">
                  <div className="panel-title">
                    <div>
                      <span className="eyebrow">✦ CREATE SOMETHING NEW</span>
                      <h2>What would you like to build?</h2>
                    </div>
                    <span className="pill">English · Urdu · Roman Urdu</span>
                  </div>
                  <label className="field-label" htmlFor="project-name">
                    PROJECT NAME
                  </label>
                  <input
                    id="project-name"
                    value={name}
                    maxLength={60}
                    onChange={(e) => setName(e.target.value)}
                  />
                  <label className="field-label" htmlFor="prompt">
                    DESCRIBE YOUR APP
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="A clothing store with a calm, minimal feel, product search and a shopping bag…"
                    rows={4}
                  />
                  <div className="prompt-toolbar">
                    <button
                      className="text-button"
                      onClick={() => fileInput.current?.click()}
                    >
                      ＋ {referenceName || "Add a reference"}
                    </button>
                    <input
                      ref={fileInput}
                      type="file"
                      accept=".pdf,.txt,.md,.json,.png,.jpg,.jpeg,.webp"
                      hidden
                      onChange={(e) =>
                        e.target.files?.[0] && upload(e.target.files[0])
                      }
                    />
                    <button
                      className="text-button"
                      onClick={dictate}
                      title="Browser speech input"
                    >
                      ◉ Dictate
                    </button>
                    <small>2 MB max</small>
                    <button
                      className="primary"
                      disabled={
                        busy ||
                        !online ||
                        prompt.trim().length < 8 ||
                        !name.trim()
                      }
                      onClick={() =>
                        action(async () => {
                          const p = await request<Project>(
                            "/projects",
                            "POST",
                            { prompt, name, reference_text: reference },
                          );
                          accept(p);
                          setTab("Requirements");
                          void request<Summary[]>("/projects").then(setProjects).catch(() => {
                            setNotice("Requirements are ready. The recent-project list could not refresh.");
                          });
                        })
                      }
                    >
                      {busy ? "Understanding…" : "Create my app"} <span>↗</span>
                    </button>
                  </div>
                  <div className="sample-row">
                    <small>TRY AN IDEA</small>
                    {samples.map((s) => (
                      <button
                        key={s.name}
                        onClick={() => {
                          setName(s.name);
                          setPrompt(s.text);
                        }}
                      >
                        {s.name} ↗
                      </button>
                    ))}
                  </div>
                </section>
              </div>
            </>
          )}
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
              <div className="pipeline-bar">
                {["prompt", "requirements", "screens", "preview", "code"].map(
                  (s, i) => (
                    <div
                      key={s}
                      className={
                        project.stage === s || tab.toLowerCase() === s
                          ? "active"
                          : ""
                      }
                    >
                      <span>
                        {project.stage === "ready" && s === "ready"
                          ? "✓"
                          : i + 1}
                      </span>
                      {s}
                    </div>
                  ),
                )}
                {active && project.status === "building" && (
                  <button
                    onClick={() =>
                      action(async () => {
                        await request(endpoint("/cancel"), "POST");
                        setNotice(
                          "Cancellation requested at the next safe checkpoint.",
                        );
                      })
                    }
                  >
                    Cancel
                  </button>
                )}
              </div>
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
              {tab === "Requirements" && (
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
                        <span
                          className="eyebrow"
                          style={{ letterSpacing: 1.5 }}
                        >
                          ✦ SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
                        </span>
                        <h2 style={{ fontSize: 25, margin: "6px 0 4px" }}>
                          Functional & Non-Functional Specifications
                        </h2>
                        <p className="subtle" style={{ margin: 0 }}>
                          Review the screen requirements and quality targets
                          before building.
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
                          href={API + endpoint("/srs.pdf")}
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
                        <p
                          className="subtle"
                          style={{ margin: "3px 0 0", fontSize: 11 }}
                        >
                          Screen plan prepared from your brief and component
                          library
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
                            <span style={{ color: "var(--purple)" }}>1.</span>{" "}
                            Functional Requirements (FR)
                          </h3>
                          <p
                            className="subtle"
                            style={{ margin: "2px 0 0", fontSize: 11 }}
                          >
                            Features and interactive actions provided by each
                            mobile screen. You can edit requirements or
                            add/remove screens freely.
                          </p>
                        </div>
                        <span className="pill">
                          {project.requirements.length} Active Screens
                        </span>
                      </div>

                      <div
                        className="requirements-list"
                        style={{ marginTop: 8 }}
                      >
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
                                <span
                                  className="id-badge"
                                  style={{ fontWeight: 700 }}
                                >
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
                                    : r.page}{" "}
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
                                  disabled={
                                    active || project.requirements.length === 1
                                  }
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
                          .filter(
                            (p) =>
                              !project.requirements.some((r) => r.page === p),
                          )
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
                          <p
                            className="subtle"
                            style={{ margin: "2px 0 0", fontSize: 11 }}
                          >
                            Performance, accessibility and persistence targets
                            to validate in the working app.
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
                        <button
                          className="secondary"
                          onClick={() => setTab("Screens")}
                        >
                          Screens customizer →
                        </button>
                        <a
                          href={API + endpoint("/srs.pdf")}
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
              )}

              {tab === "Preview" && (
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
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 8 }}
                    >
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
                          .map(
                            (p, i) =>
                              `${i + 1}. ${p === "products" ? "Catalog" : p}`,
                          )
                          .join("  ·  ")}
                      </span>
                    </div>
                    <div
                      style={{ color: "var(--soft, #646b79)", fontSize: 10 }}
                    >
                      {device === "desktop"
                        ? "Desktop · 1280px viewport"
                        : device === "tablet"
                          ? "Tablet · 820px viewport"
                          : "Phone · 375px viewport"}{" "}
                      ·{" "}
                      {showWorkingApp
                        ? "Working generated app"
                        : "Design preview"}
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
                            page={
                              previewScreen ||
                              project.requirements[0]?.page ||
                              "home"
                            }
                            configs={screenConfigs}
                            onSelect={setPreviewScreen}
                            device={device}
                          />
                        ) : (
                          <PreviewDevice device={device}>
                            <div className="device-top">
                              <i />
                              <span>
                                JINIE WORKING APP · {device.toUpperCase()}
                              </span>
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
                          The working app uses the last successful build. Accept
                          screens again to rebuild your changes.
                        </p>
                      )}
                    </>
                  ) : (
                    <div className="empty-stage">
                      <div
                        className={"small-orb " + (active ? "spinning" : "")}
                      >
                        ✦
                      </div>
                      <h2>
                        {active
                          ? "Your idea is taking shape."
                          : "Your preview starts with a build."}
                      </h2>
                      <p>
                        Approve the brief and generate your app to explore the
                        real output.
                      </p>
                    </div>
                  )}
                </>
              )}
              {tab === "Code" && (
                <section className="panel code-panel">
                  <div className="panel-title">
                    <div>
                      <h2>Source explorer</h2>
                      <small className="subtle">
                        {dirty ? "Unsaved edits" : file} · JSX / JSON /
                        JavaScript
                      </small>
                    </div>
                    <div className="button-row">
                      <button
                        className="secondary"
                        disabled={!dirty || active || busy}
                        onClick={() =>
                          action(async () => {
                            accept(
                              await request(
                                endpoint(
                                  "/file?path=" + encodeURIComponent(file),
                                ),
                                "PUT",
                                { content: code },
                              ),
                            );
                            setDirty(false);
                            setNotice(
                              "Source saved. Rebuild to refresh the preview.",
                            );
                          })
                        }
                      >
                        Save file
                      </button>
                      <button
                        className="primary"
                        disabled={dirty || active || busy || !files.length}
                        onClick={() =>
                          action(async () => {
                            accept(await request(endpoint("/rebuild"), "POST"));
                            setTab("Preview");
                          })
                        }
                      >
                        Rebuild source ↗
                      </button>
                    </div>
                  </div>
                  <div
                    className="button-row"
                    aria-label="Requirements linked to this file"
                  >
                    {project.traceability
                      .filter((link) => link.files.includes(file))
                      .map((link) => (
                        <button
                          key={link.requirement}
                          className="id-badge"
                          onClick={() => {
                            if (
                              dirty &&
                              !confirm("Discard unsaved file edits?")
                            )
                              return;
                            setDirty(false);
                            setFocusedRequirement(link.requirement);
                            setTab("Requirements");
                          }}
                        >
                          {link.requirement} · {link.page}
                        </button>
                      ))}
                    {!project.traceability.some((link) =>
                      link.files.includes(file),
                    ) && (
                      <small className="subtle">
                        No requirement link recorded for this file.
                      </small>
                    )}
                  </div>
                  <div className="code-layout">
                    <div className="file-tree">
                      <FileTree
                        files={files}
                        current={file}
                        onSelect={(f) => {
                          if (dirty && !confirm("Discard unsaved file edits?"))
                            return;
                          setFile(f);
                        }}
                      />
                    </div>
                    <Editor
                      className="source-editor"
                      textareaId="source-code"
                      value={code}
                      disabled={active}
                      onValueChange={(value) => {
                        setCode(value);
                        setDirty(true);
                      }}
                      highlight={(value) =>
                        Prism.highlight(
                          value,
                          Prism.languages[
                            file.endsWith(".json") ? "json" : "jsx"
                          ],
                          "jsx",
                        )
                      }
                      padding={18}
                      style={{
                        fontFamily: "Consolas, monospace",
                        fontSize: 11,
                        minHeight: 600,
                      }}
                    />
                  </div>
                  {!files.length && (
                    <p>Generate the project to explore its source.</p>
                  )}
                </section>
              )}
              {tab === "Evidence" && (
                <>
                  <div className="evidence-stats">
                    <div className="panel">
                      <strong>{project.traceability.length}</strong>
                      <span>Linked requirements</span>
                    </div>
                    <div className="panel">
                      <strong>
                        {
                          project.tests.filter((t) => t.status === "passed")
                            .length
                        }
                      </strong>
                      <span>Checks passed</span>
                    </div>
                    <div className="panel">
                      <strong>
                        {
                          (
                            project.rag_components ||
                            project.spec?.rag_components ||
                            []
                          ).length
                        }
                      </strong>
                      <span>Catalog matches</span>
                    </div>
                    <div className="panel">
                      <strong>
                        {
                          project.tests.filter((t) => t.status === "not_run")
                            .length
                        }
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
                                      if (
                                        dirty &&
                                        !confirm("Discard unsaved file edits?")
                                      )
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
                  <RetrievedComponents
                    components={
                      project.rag_components ||
                      project.spec.rag_components ||
                      []
                    }
                  />
                  <section className="panel">
                    <h2>Validation, with context.</h2>
                    <p className="subtle">
                      Structural checks and compilation are automated. They do
                      not establish model accuracy or replace testing the app on
                      a phone.
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
                      ProductCard is used by the generated app. Other catalog
                      components are exported starter templates.
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
              )}
              {tab === "Deploy" && (
                <section className="panel deploy-panel">
                  <div className="small-orb">↗</div>
                  <span className="eyebrow">TAKE IT FURTHER</span>
                  <h2>A build you can take with you.</h2>
                  <p>
                    Download the React Native source for Expo and device
                    testing, or publish its browser build to your configured
                    Firebase Hosting project.
                  </p>
                  <div className="deploy-cards">
                    <div>
                      <span>01 / NATIVE PROJECT</span>
                      <h3>Open it. Run it. Make it yours.</h3>
                      <p>
                        Includes source, app configuration, sample catalog,
                        traceability and build checks.
                      </p>
                      {current ? (
                        <a
                          className="primary"
                          href={API + endpoint("/download")}
                        >
                          Download ZIP ↓
                        </a>
                      ) : (
                        <small>Finish a current build first.</small>
                      )}
                    </div>
                    <div>
                      <span>02 / FIREBASE HOSTING</span>
                      <h3>Share the browser experience.</h3>
                      <p>
                        Requires Firebase CLI login and JINIE_FIREBASE_PROJECT
                        on the backend. Hosting publishes the web build; it does
                        not install a native app.
                      </p>
                      <button
                        className="secondary"
                        disabled={!current || busy || active}
                        onClick={() =>
                          action(async () =>
                            accept(await request(endpoint("/deploy"), "POST")),
                          )
                        }
                      >
                        Deploy to Firebase ↗
                      </button>
                    </div>
                  </div>
                  {project.deployment && (
                    <div className="alert">
                      <a
                        href={project.deployment.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {project.deployment.url}
                      </a>
                      <span>{project.deployment.time}</span>
                    </div>
                  )}
                </section>
              )}
              <details className="panel live-logs" open={active}>
                <summary>
                  <span className="tiny-dot" /> Engine activity{" "}
                  <small>{project.events.length} events</small>
                </summary>
                <div role="log">
                  {project.events.map((e) => (
                    <div key={e.id}>
                      <time>{new Date(e.time).toLocaleTimeString()}</time>
                      <b>{e.stage}</b>
                      <span>{e.message}</span>
                    </div>
                  ))}
                </div>
              </details>
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
