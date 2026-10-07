import { useEffect, useRef, useState } from "react";
import { useStudioAppearance } from "../../hooks/useStudioAppearance";
import type { Requirement, Design, Project, Summary } from "./types";
import { type User } from "../../components/auth/AuthModal";
import type { ScreenConfigData } from "../live_review_panel/HtmlScreenMockup";
import { API, request, samples, authHeaders, ensureGuest } from "./studioApi";
// Shared controller: owns project state, approvals, API actions and polling; panel components reuse these callbacks.
export default function useStudioController() {
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
  useEffect(() => {
    const requireLogin = (event: Event) => {
      setNotice((event as CustomEvent<string>).detail);
      setAuthOpen(true);
    };
    window.addEventListener("jinie-login-required", requireLogin);
    return () => window.removeEventListener("jinie-login-required", requireLogin);
  }, []);
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
  const showWorkingApp = project?.build_revision != null;
  const [device, setDevice] = useState(() => {
      try {
      const saved = localStorage.getItem("jinie_preview_device");
      return saved === "tablet" || saved === "desktop" ? saved : "mobile";
      } catch { return "mobile"; }
    }),
    [previewScreen, setPreviewScreen] = useState("");
  useEffect(() => {
    try { localStorage.setItem("jinie_preview_device", device); } catch { /* Preferences still work for this session. */ }
  }, [device]);
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
    try {
      localStorage.setItem("jinie_project_id", p.id);
    } catch {
      /* Project is still available in this session. */
    }
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
  // Acceptance flow: saves approved requirements and refinements, starts the build, then opens Preview.
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
            else if (alive) {
              setUser(null);
              setProject(null);
              setProjects([]);
              localStorage.removeItem("jinie_user");
              localStorage.removeItem("jinie_auth_token");
              localStorage.removeItem("jinie_asset_token");
            }
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
        if (alive) setError("Backend is offline. Please try again.");
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
    localStorage.removeItem("jinie_asset_token");
    localStorage.removeItem("jinie_project_id");
    setProject(null); setProjects([]);
    setUser(null);
    setTab("Prompt");
    setNotice("Signed out successfully.");
  }
  useEffect(() => {
    if (!user) return;
    let alive = true;
    request<Summary[]>("/projects").then((items) => {
      if (alive) setProjects(items);
    }).catch(() => {});
    return () => { alive = false; };
  }, [user?.id]);
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
  // Speech input: uses the browser SpeechRecognition API and appends the recognized transcript to the prompt.
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
      if (!localStorage.getItem("jinie_auth_token")) await ensureGuest();
      const data = new FormData();
      data.append("file", f);
      const r = await fetch(API + "/references", {
        headers: authHeaders(),
        method: "POST",
        body: data,
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail);
      setReference(body.text);
      setReferenceName(body.name);
    });
  }

  return {
    appearance,
    project,
    setProject,
    projects,
    setProjects,
    tab,
    setTab,
    user,
    setUser,
    authOpen,
    setAuthOpen,
    refinePrompt,
    setRefinePrompt,
    screenConfigs,
    setScreenConfigs,
    prompt,
    setPrompt,
    name,
    setName,
    reference,
    setReference,
    referenceName,
    setReferenceName,
    busy,
    setBusy,
    error,
    setError,
    online,
    setOnline,
    files,
    setFiles,
    file,
    setFile,
    code,
    setCode,
    dirty,
    setDirty,
    component,
    setComponent,
    focusedRequirement,
    setFocusedRequirement,
    showWorkingApp,
    device,
    setDevice,
    previewScreen,
    setPreviewScreen,
    notice,
    setNotice,
    reviewDirty,
    setReviewDirty,
    fileInput,
    actionRunning,
    active,
    current,
    endpoint,
    action,
    accept,
    mergeScreenConfig,
    handleUpdateScreenConfig,
    handleUpdateRequirementText,
    applyScreenRefinement,
    handleApproveAndBuild,
    handleRefineScreens,
    logout,
    updateRequirement,
    design,
    saveReview,
    dictate,
    upload,
  };
}
export type StudioContext = ReturnType<typeof useStudioController>;
