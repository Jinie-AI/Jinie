import type { Project, Summary } from "../shared/types";
import PromptHero from "./PromptHero";
import { request, samples } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
export default function InputInterface({
  appearance,
  setProjects,
  setTab,
  prompt,
  setPrompt,
  name,
  setName,
  reference,
  referenceName,
  busy,
  online,
  setNotice,
  fileInput,
  action,
  accept,
  dictate,
  upload,
}: Pick<
  StudioContext,
  | "appearance"
  | "project"
  | "projects"
  | "setProjects"
  | "setTab"
  | "prompt"
  | "setPrompt"
  | "name"
  | "setName"
  | "reference"
  | "referenceName"
  | "busy"
  | "online"
  | "files"
  | "file"
  | "setNotice"
  | "fileInput"
  | "current"
  | "action"
  | "accept"
  | "dictate"
  | "upload"
>) {
  return (
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
              onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
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
                busy || !online || prompt.trim().length < 8 || !name.trim()
              }
              onClick={() =>
                action(async () => {
                  const p = await request<Project>("/projects", "POST", {
                    prompt,
                    name,
                    reference_text: reference,
                  });
                  accept(p);
                  setTab("Requirements");
                  void request<Summary[]>("/projects")
                    .then(setProjects)
                    .catch(() => {
                      setNotice(
                        "Requirements are ready. The recent-project list could not refresh.",
                      );
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
  );
}
