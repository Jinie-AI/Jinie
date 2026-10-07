import { useState } from "react";
import type { ScreenConfigData } from "./HtmlScreenMockup";
import DesignPreview from "./DesignPreview";
import DesignControls from "../design_preferences_panel/DesignControls";
import type { Design, Project } from "../shared/types";
import "../../styles/screens-workspace.css";

interface Props {
  project: Project;
  screenConfigs: Record<string, ScreenConfigData>;
  onUpdateScreenConfig: (
    page: string,
    config: Partial<ScreenConfigData>,
  ) => void;
  onUpdateRequirement: (page: string, text: string) => void;
  onUpdateDesign: (change: Partial<Design>) => void;
  onBuildApp: () => void;
  onSave: () => void;
  onRefine: () => void;
  refinement: string;
  onRefinementChange: (value: string) => void;
  dirty: boolean;
  busy: boolean;
  active: boolean;
}

const labelFor = (page: string) =>
  page === "products"
    ? "Catalog"
    : page
        .replace(/^custom_/, "")
        .replaceAll("_", " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());

// Screens workspace: previews proposed layouts and collects design refinements before the working app is built.
export default function ScreenShowcaseSection({
  project,
  screenConfigs,
  onUpdateScreenConfig,
  onUpdateRequirement,
  onUpdateDesign,
  onBuildApp,
  onSave,
  onRefine,
  refinement,
  onRefinementChange,
  dirty,
  busy,
  active,
}: Props) {
  const pages = project.requirements.map((item) => item.page);
  const [selected, setSelected] = useState(pages[0] || "home");
  const [view, setView] = useState<"single" | "gallery">("single");
  const selectedScreen = pages.includes(selected) ? selected : pages[0];
  const currentConfig = screenConfigs[selectedScreen] || {};
  const currentRequirement = project.requirements.find(
    (item) => item.page === selectedScreen,
  );
  const disabled = busy || active;
  const invalidPrompt = !!refinement.trim() && refinement.trim().length < 8;
  const mockup = (page: string) => (
    <DesignPreview
      project={project}
      page={page}
      configs={screenConfigs}
      onSelect={(next) => {
        setSelected(next);
        setView("single");
      }}
    />
  );

  return (
    <div className="screens-workspace">
      <section className="panel screens-toolbar">
        <div>
          <span className="eyebrow">REVIEW · CUSTOMIZE · BUILD</span>
          <h2>Your screens, your direction.</h2>
          <p className="subtle">
            Review {pages.length} screens, adjust the appearance, then accept to
            build your working preview.
          </p>
        </div>
        <button
          type="button"
          className="primary"
          disabled={disabled || invalidPrompt}
          onClick={onBuildApp}
        >
          {active
            ? "Building…"
            : busy
              ? "Saving changes…"
              : "Accept screens & build preview ↗"}
        </button>
      </section>

      <div className="screens-layout">
        <aside
          className="panel screens-controls"
          aria-label="Screen and design controls"
        >
          <section className="screen-refinement">
            <span className="eyebrow">REFINE YOUR APP</span>
            <h3>Describe a change.</h3>
            <label className="screen-field" htmlFor="screen-refinement">
              Change colors, layouts or screen copy
            </label>
            <textarea
              id="screen-refinement"
              rows={4}
              value={refinement}
              disabled={disabled}
              onChange={(event) => onRefinementChange(event.target.value)}
              placeholder="Use warm terracotta colors, serif headings, and an editorial catalog."
            />
            {invalidPrompt && (
              <small className="subtle">
                Add a little more detail (at least 8 characters).
              </small>
            )}
            <button
              type="button"
              className="secondary"
              disabled={disabled || refinement.trim().length < 8}
              onClick={onRefine}
            >
              {busy ? "Applying…" : "Apply prompt to screens"}
            </button>
            <p className="subtle">
              Review the updated screens here before building. Screen features
              are managed in Requirements.
            </p>
          </section>

          <DesignControls
            design={project.design}
            recommendations={project.recommendations}
            onChange={onUpdateDesign}
            disabled={disabled}
          />

          <fieldset className="screen-specific-controls" disabled={disabled}>
            <legend>{labelFor(selectedScreen)} screen</legend>
            <label className="screen-field">
              Screen title
              <input
                value={currentConfig.title || ""}
                maxLength={100}
                onChange={(event) =>
                  onUpdateScreenConfig(selectedScreen, {
                    title: event.target.value,
                  })
                }
                placeholder={labelFor(selectedScreen)}
              />
            </label>
            <label className="screen-field">
              Subtitle
              <textarea
                rows={2}
                maxLength={200}
                value={currentConfig.subtitle || ""}
                onChange={(event) =>
                  onUpdateScreenConfig(selectedScreen, {
                    subtitle: event.target.value,
                  })
                }
              />
            </label>
            {["home", "products", "search"].includes(selectedScreen) && (
              <label className="screen-field">
                Screen composition
                <select
                  value={currentConfig.layout || project.design.layout}
                  onChange={(event) =>
                    onUpdateScreenConfig(selectedScreen, {
                      layout: event.target.value as ScreenConfigData["layout"],
                    })
                  }
                >
                  <option value="grid">Grid</option>
                  <option value="editorial">Editorial</option>
                  <option value="cards">Horizontal cards</option>
                </select>
              </label>
            )}
            {selectedScreen === "home" && (
              <label className="screen-toggle">
                Hero section
                <input
                  type="checkbox"
                  checked={currentConfig.show_hero !== false}
                  onChange={(event) =>
                    onUpdateScreenConfig(selectedScreen, {
                      show_hero: event.target.checked,
                    })
                  }
                />
              </label>
            )}
            {["home", "products", "search"].includes(selectedScreen) && (
              <label className="screen-toggle">
                Search field
                <input
                  type="checkbox"
                  checked={currentConfig.show_search !== false}
                  onChange={(event) =>
                    onUpdateScreenConfig(selectedScreen, {
                      show_search: event.target.checked,
                    })
                  }
                />
              </label>
            )}
            <label className="screen-toggle">
              Product badges
              <input
                type="checkbox"
                checked={currentConfig.show_badges !== false}
                onChange={(event) =>
                  onUpdateScreenConfig(selectedScreen, {
                    show_badges: event.target.checked,
                  })
                }
              />
            </label>
            {currentRequirement && (
              <details className="screen-requirement">
                <summary>Screen requirement · {currentRequirement.id}</summary>
                <textarea
                  aria-label={selectedScreen + " requirement"}
                  rows={4}
                  maxLength={1000}
                  value={currentRequirement.text}
                  onChange={(event) =>
                    onUpdateRequirement(selectedScreen, event.target.value)
                  }
                />
                <p className="subtle">
                  Editing this description updates the specification; use the
                  controls above to change the appearance.
                </p>
              </details>
            )}
          </fieldset>
          <div className="screens-save">
            <span>{dirty ? "Unsaved changes" : "All changes saved"}</span>
            <button
              type="button"
              className="secondary"
              onClick={onSave}
              disabled={disabled || !dirty}
            >
              Save changes
            </button>
          </div>
        </aside>

        <section className="screens-canvas" aria-label="Screen previews">
          <div className="screens-canvas-toolbar">
            <div className="screen-tabs" aria-label="Choose a screen">
              {pages.map((page, index) => (
                <button
                  type="button"
                  key={page}
                  aria-pressed={selectedScreen === page}
                  className={selectedScreen === page ? "chosen" : ""}
                  onClick={() => {
                    setSelected(page);
                    setView("single");
                  }}
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {labelFor(page)}
                </button>
              ))}
            </div>
            <div className="segmented">
              <button
                type="button"
                className={view === "single" ? "chosen" : ""}
                onClick={() => setView("single")}
              >
                Single screen
              </button>
              <button
                type="button"
                className={view === "gallery" ? "chosen" : ""}
                onClick={() => setView("gallery")}
              >
                All screens
              </button>
            </div>
          </div>
          {view === "single" ? (
            <div className="screen-preview-stage">
              <span className="eyebrow">
                {labelFor(selectedScreen)} · DESIGN PREVIEW
              </span>
              {mockup(selectedScreen)}
              <p className="subtle">
                Review your design here. The same accepted design is shown in
                Preview.
              </p>
            </div>
          ) : (
            <div className="screen-gallery">
              {pages.map((page) => (
                <article className="screen-gallery-item" key={page}>
                  <div>
                    <h3>{labelFor(page)}</h3>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => {
                        setSelected(page);
                        setView("single");
                      }}
                    >
                      Customize ↗
                    </button>
                  </div>
                  {mockup(page)}
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
