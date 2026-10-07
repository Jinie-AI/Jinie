import { useEffect, useRef, useState } from "react";
import type { User } from "../../components/auth/AuthModal";
import type { StudioContext } from "../shared/useStudioController";
import { API, authHeaders, request } from "../shared/studioApi";
import "./account-settings.css";

// Account settings use the authenticated backend; workspace preferences reuse the existing appearance controls.
export default function AccountSettings({ user, setUser, appearance, device, setDevice, logout, projects, action, accept, setTab, setDirty, dirty, reviewDirty }: StudioContext) {
  const [fullName, setFullName] = useState(user?.full_name || "");
  const photoInput = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  useEffect(() => {
    let alive = true;
    request<{ user: User }>("/auth/me").then(({ user: fresh }) => {
      if (!alive) return;
      setUser(fresh); setFullName(fresh.full_name);
      localStorage.setItem("jinie_user", JSON.stringify(fresh));
    }).catch((error) => { if (alive) setError(error.message); });
    return () => { alive = false; };
  }, [setUser]);
  if (!user) return null;
  async function save(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await request<{ user: User }>("/auth/profile", "PUT", { full_name: fullName.trim() });
      setUser(result.user);
      localStorage.setItem("jinie_user", JSON.stringify(result.user));
      setMessage("Profile updated successfully.");
    } catch (error) { setError(error instanceof Error ? error.message : "Could not update profile."); }
    finally { setBusy(false); }
  }
  async function uploadPhoto(file?: File) {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { setError("Choose an image smaller than 5 MB."); return; }
    setBusy(true); setError(""); setMessage("");
    try {
      const body = new FormData(); body.append("file", file);
      const response = await fetch(API + "/auth/profile/photo", { method: "POST", headers: authHeaders(), body });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Could not upload this photo.");
      setUser(result.user);
      localStorage.setItem("jinie_user", JSON.stringify(result.user));
      setMessage("Profile photo updated successfully.");
    } catch (error) { setError(error instanceof Error ? error.message : "Could not upload photo."); }
    finally { setBusy(false); }
  }
  async function resetPassword() {
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await request<{ message: string }>("/auth/reset-password", "POST", { email: user!.email });
      setMessage(result.message);
    } catch (error) { setError(error instanceof Error ? error.message : "Could not send password reset."); }
    finally { setBusy(false); }
  }
  const methods = user.sign_in_methods || [];
  const photoSource = user.photo_url?.startsWith("/api/auth/avatars/")
    ? API.replace(/\/api$/, "") + user.photo_url
    : user.photo_url?.startsWith("https://") ? user.photo_url : undefined;
  const matches = projects.filter((project) => project.name.toLowerCase().includes(query.toLowerCase()));
  return <section className="account-settings">
    <div className="workspace-heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Your account.</h1><p>Manage your profile, security and workspace preferences.</p></div></div>
    {error && <div className="alert error" role="alert">{error}</div>}
    {message && <div className="alert" role="status">{message}</div>}
    <div className="account-grid">
      <section className="account-card">
        <h2>Profile</h2>
        <div className="account-identity">
          <button type="button" className="account-avatar account-avatar-picker" disabled={busy} onClick={() => photoInput.current?.click()} aria-label="Choose a new profile photo" title="Choose a new profile photo"><span>{user.initials}</span>{photoSource && <img key={photoSource} src={photoSource} alt="" referrerPolicy="no-referrer" onError={(event) => { event.currentTarget.hidden = true; }} />}<span className="account-avatar-edit" aria-hidden="true">✎</span></button>
          <input ref={photoInput} type="file" accept="image/jpeg,image/png,image/webp" hidden aria-label="Profile photo file" onChange={(event) => { void uploadPhoto(event.target.files?.[0]); event.target.value = ""; }} />
          <div><strong>{user.full_name}</strong><p>{user.email}</p><span className={"account-status " + (user.email_verified ? "verified" : "")}>{user.email_verified ? "✓ Email verified" : "Local account"}</span></div>
        </div>
        <p className="subtle account-photo-hint">Click your photo to change it. JPG, PNG or WebP · up to 5 MB.</p>
        <form onSubmit={save} className="account-form">
          <label htmlFor="profile-name">Full name</label>
          <input id="profile-name" required minLength={2} maxLength={100} value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" />
          <label htmlFor="profile-email">Email address</label>
          <input id="profile-email" value={user.email} readOnly type="email" />
          <button className="primary" type="submit" disabled={busy || fullName.trim() === user.full_name}>{busy ? "Saving…" : "Save profile"}</button>
        </form>
      </section>
      <div className="account-column">
        <section className="account-card">
          <h2>Account security</h2>
          <p className="subtle">Sign-in method</p>
          <div className="account-methods">{methods.length ? methods.map((method) => <span key={method}>{method === "google.com" ? "Google" : method === "password" ? "Email & password" : method}</span>) : <span>Email & password</span>}</div>
          {methods.includes("password") ? <button type="button" className="secondary" disabled={busy} onClick={resetPassword}>Send password reset email</button> : methods.includes("google.com") ? <a className="secondary" href="https://myaccount.google.com/security" target="_blank" rel="noreferrer">Manage Google account security ↗</a> : <p className="subtle">Password recovery is available for Firebase email accounts.</p>}
          <button type="button" className="text-button account-signout" onClick={logout}>Sign out of Jinie</button>
        </section>
        <section className="account-card">
          <h2>Workspace preferences</h2>
          <div className="account-form">
            <label htmlFor="account-theme">Appearance</label>
            <select id="account-theme" value={appearance.theme} onChange={(event) => appearance.setTheme(event.target.value as "light" | "dark" | "system")}><option value="system">Follow system</option><option value="light">Light</option><option value="dark">Dark</option></select>
            <label htmlFor="account-device">Default preview device</label>
            <select id="account-device" value={device} onChange={(event) => setDevice(event.target.value)}><option value="mobile">Mobile</option><option value="tablet">Tablet</option><option value="desktop">Desktop</option></select>
            <label className="account-toggle"><input type="checkbox" checked={appearance.motion} onChange={(event) => appearance.setMotion(event.target.checked)} /> Enable workspace animations</label>
            <p className="subtle">Preferences are saved automatically in this browser.</p>
          </div>
        </section>
      </div>
    </div>
    <section className="account-card account-projects">
      <div className="account-project-heading"><h2>My projects <small>{projects.length}</small></h2><input aria-label="Search my projects" placeholder="Search projects…" type="search" value={query} onChange={(event) => setQuery(event.target.value)} /></div>
      {matches.length ? <div className="account-project-list">{matches.map((project) => <button key={project.id} type="button" onClick={() => action(async () => {
        if ((dirty || reviewDirty) && !confirm("Discard unsaved edits?")) return;
        const selected = await request<Parameters<typeof accept>[0]>("/projects/" + project.id);
        accept(selected); setDirty(false); setTab("Requirements");
      })}><div><strong>{project.name}</strong>{project.updated_at && <small>{new Date(project.updated_at).toLocaleDateString()}</small>}</div><span>{project.status} ↗</span></button>)}</div> : <p className="subtle">{query ? "No matching projects." : "Your projects will appear here once you create an app."}</p>}
    </section>
  </section>;
}
