import { API, request } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
export default function DeployDashboard({
  project,
  busy,
  active,
  current,
  endpoint,
  action,
  accept,
}: Pick<
  StudioContext,
  | "project"
  | "busy"
  | "device"
  | "active"
  | "current"
  | "endpoint"
  | "action"
  | "accept"
>) {
  if (!project) return null;
  return (
    <section className="panel deploy-panel">
      <div className="small-orb">↗</div>
      <span className="eyebrow">TAKE IT FURTHER</span>
      <h2>A build you can take with you.</h2>
      <p>
        Download the React Native source for Expo and device testing, or publish
        its browser build to your configured Firebase Hosting project.
      </p>
      <div className="deploy-cards">
        <div>
          <span>01 / NATIVE PROJECT</span>
          <h3>Open it. Run it. Make it yours.</h3>
          <p>
            Includes source, app configuration, sample catalog, traceability and
            build checks.
          </p>
          {current ? (
            <a className="primary" href={API + endpoint("/download")}>
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
            Requires Firebase CLI login and JINIE_FIREBASE_PROJECT on the
            backend. Hosting publishes the web build; it does not install a
            native app.
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
          <a href={project.deployment.url} target="_blank" rel="noreferrer">
            {project.deployment.url}
          </a>
          <span>{project.deployment.time}</span>
        </div>
      )}
    </section>
  );
}
