import { useEffect, useState } from "react";

type Settings = {
  expo_project_id: string;
  owner: string;
  slug: string;
  android_package: string;
  ios_bundle: string;
  asc_app_id: string;
  credentials_ready: boolean;
};
type Deployment = {
  settings: Settings | null;
  checks: Record<string, string[]>;
  job?: {
    state: string;
    message: string;
    builds: { platform: string; url: string }[];
  } | null;
};
const empty: Settings = {
  expo_project_id: "",
  owner: "",
  slug: "",
  android_package: "",
  ios_bundle: "",
  asc_app_id: "",
  credentials_ready: false,
};
export default function MobileDeployment({
  api,
  projectId,
  current,
  onStarted,
}: {
  api: string;
  projectId: string;
  current: boolean;
  onStarted: () => void;
}) {
  const [data, setData] = useState<Deployment | null>(null);
  const [settings, setSettings] = useState<Settings>(empty);
  const [platform, setPlatform] = useState("android");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [dirty, setDirty] = useState(false);
  const endpoint = api + "/projects/" + projectId + "/mobile-deployment";
  async function call(url: string, method = "GET", body?: unknown) {
    const r = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const d = await r.json();
    if (!r.ok)
      throw new Error(
        typeof d.detail === "string"
          ? d.detail
          : "Check the app identifiers and required fields.",
      );
    return d as Deployment;
  }
  useEffect(() => {
    let alive = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const d = await call(endpoint);
        if (alive) {
          setData(d);
          timer = setTimeout(poll, 3000);
        }
      } catch (e) {
        if (alive)
          setError(e instanceof Error ? e.message : "Connection failed");
      }
    }
    void call(endpoint)
      .then((d) => {
        if (alive) {
          setSettings(d.settings || empty);
          setData(d);
          timer = setTimeout(poll, 3000);
        }
      })
      .catch((e) => {
        if (alive) setError(String(e));
      });
    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [endpoint]);
  const running = ["queued", "building", "submitting"].includes(
    data?.job?.state || "",
  );
  const issues = data?.checks[platform] || [];
  async function save() {
    setBusy(true);
    setError("");
    try {
      setData(await call(endpoint + "/settings", "PUT", settings));
      setDirty(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save");
    } finally {
      setBusy(false);
    }
  }
  async function submit() {
    setBusy(true);
    setError("");
    try {
      setData(await call(endpoint, "POST", { platform }));
      onStarted();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start");
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel mobile-deployment">
      <span className="eyebrow">03 / APP STORES</span>
      <h3>Build & submit your mobile app.</h3>
      <p>
        Upload signed builds to Google Play internal testing or Apple
        TestFlight. Store processing, review and public release follow
        separately.
      </p>
      <details open={!data?.settings}>
        <summary>One-time project setup</summary>
        <p>
          Link an existing Expo project and configure signing and store
          credentials with EAS on the backend machine. Keep account tokens and
          private keys out of these fields.
        </p>
        <div className="mobile-settings-grid">
          {(
            [
              ["expo_project_id", "Expo project ID (UUID)"],
              ["owner", "Expo account or organization"],
              ["slug", "Expo project slug"],
              ["android_package", "Android package (com.example.app)"],
              ["ios_bundle", "iOS bundle identifier"],
              ["asc_app_id", "App Store Connect numeric app ID"],
            ] as const
          ).map(([key, label]) => (
            <label key={key}>
              {label}
              <input
                value={settings[key]}
                disabled={busy || running}
                onChange={(e) => {
                  setSettings({ ...settings, [key]: e.target.value });
                  setDirty(true);
                }}
              />
            </label>
          ))}
        </div>
        <label>
          <input
            type="checkbox"
            checked={settings.credentials_ready}
            disabled={busy || running}
            onChange={(e) => {
              setSettings({ ...settings, credentials_ready: e.target.checked });
              setDirty(true);
            }}
          />{" "}
          I have configured signing and store credentials in EAS.
        </label>
        <button className="secondary" disabled={busy || running} onClick={save}>
          Save store setup
        </button>
      </details>
      <label>
        Destination
        <select
          value={platform}
          disabled={busy || running}
          onChange={(e) => setPlatform(e.target.value)}
        >
          <option value="android">Google Play · Internal testing</option>
          <option value="ios">Apple · TestFlight</option>
          <option value="all">Both stores · Testing</option>
        </select>
      </label>
      {issues.length > 0 && (
        <ul>
          {issues.map((issue) => (
            <li key={issue}>{issue}</li>
          ))}
        </ul>
      )}
      {dirty && <p>Save your setup changes before submitting.</p>}
      <button
        className="primary"
        disabled={
          !data || !current || busy || running || dirty || issues.length > 0
        }
        onClick={submit}
      >
        {running ? "Deployment in progress…" : "Build & submit ↗"}
      </button>
      {error && <p role="alert">{error}</p>}
      {data?.job && (
        <div role="status">
          <strong>{data.job.state}</strong>
          <p>{data.job.message}</p>
          {data.job.builds.map((build) => (
            <p key={build.url}>
              <a href={build.url} target="_blank" rel="noreferrer">
                Open {build.platform} build in Expo ↗
              </a>
            </p>
          ))}
        </div>
      )}
    </section>
  );
}
