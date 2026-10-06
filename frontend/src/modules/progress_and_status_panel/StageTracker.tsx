import { request } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
export default function StageTracker({
  project,
  tab,
  setNotice,
  active,
  endpoint,
  action,
}: Pick<
  StudioContext,
  | "project"
  | "tab"
  | "prompt"
  | "code"
  | "setNotice"
  | "active"
  | "endpoint"
  | "action"
>) {
  if (!project) return null;
  return (
    <div className="pipeline-bar">
      {["prompt", "requirements", "screens", "preview", "code"].map((s, i) => (
        <div
          key={s}
          className={
            project.stage === s || tab.toLowerCase() === s ? "active" : ""
          }
        >
          <span>
            {project.stage === "ready" && s === "ready" ? "✓" : i + 1}
          </span>
          {s}
        </div>
      ))}
      {active && project.status === "building" && (
        <button
          onClick={() =>
            action(async () => {
              await request(endpoint("/cancel"), "POST");
              setNotice("Cancellation requested at the next safe checkpoint.");
            })
          }
        >
          Cancel
        </button>
      )}
    </div>
  );
}
