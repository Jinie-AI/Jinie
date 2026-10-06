import type { StudioContext } from "../shared/useStudioController";
export default function LiveLogStream({
  project,
  active,
}: Pick<StudioContext, "project" | "active">) {
  if (!project) return null;
  return (
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
  );
}
