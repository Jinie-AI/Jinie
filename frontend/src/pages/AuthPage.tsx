import { authHeaders } from "../modules/shared/studioApi";
import GoogleSignIn, { type AuthSession } from "../components/auth/GoogleSignIn";
import VerificationNotice from "../components/auth/VerificationNotice";
import AuthRecovery from "../components/auth/AuthRecovery";
import BrandLogo from "../components/BrandLogo";
import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import "../styles/studio.css";
import "../styles/appearance.css";

const API =
  (
    import.meta.env.VITE_API_URL ||
    (typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
      ? ""
      : "http://127.0.0.1:8000")
  ).replace(/\/$/, "") + "/api";

export default function AuthPage({
  defaultMode = "login",
}: {
  defaultMode?: "login" | "signup";
}) {
  const [emailOrUser, setEmailOrUser] = useState("");
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [verificationTicket, setVerificationTicket] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();
  const location = useLocation();

  const mode =
    location.pathname === "/signup"
      ? "signup"
      : location.pathname === "/login"
        ? "login"
        : defaultMode;

  function finishSession(session: AuthSession) {
    localStorage.setItem("jinie_asset_token", session.asset_token || "");
    localStorage.setItem("jinie_user", JSON.stringify(session.user));
    localStorage.setItem("jinie_auth_token", session.token);
    setVerificationTicket("");
    setSuccess("Signed in successfully! Redirecting...");
    navigate("/");
  }
  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!emailOrUser.trim() || !password) {
      setError("Please provide your email and password.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({
          email_or_username: emailOrUser.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      localStorage.setItem("jinie_asset_token", data.asset_token || "");
      localStorage.setItem("jinie_user", JSON.stringify(data.user));
      localStorage.setItem("jinie_auth_token", data.token);
      setSuccess("Signed in successfully! Redirecting...");
      setTimeout(() => navigate("/"), 600);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    if (!fullName.trim() || !username.trim() || !email.trim() || !password) {
      setError("Please fill out all required fields.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/signup`, {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName.trim(),
          username: username.trim(),
          email: email.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      if (data.verification_required) { setNotice(""); setVerificationTicket(data.verification_ticket); setPassword(""); setConfirmPassword(""); return; }
      localStorage.setItem("jinie_asset_token", data.asset_token || "");
      localStorage.setItem("jinie_user", JSON.stringify(data.user));
      localStorage.setItem("jinie_auth_token", data.token);
      setSuccess("Account created! Redirecting to workspace...");
      setTimeout(() => navigate("/"), 600);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page-wrapper">
      <div className="auth-page-card">
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <Link
            to="/"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              textDecoration: "none",
            }}
          >
            <BrandLogo />
          </Link>
          <h2
            style={{
              fontSize: 22,
              margin: "10px 0 6px",
              fontFamily: "Manrope, system-ui",
              fontWeight: 700,
            }}
          >
            {mode === "login" ? "Sign In to Workspace" : "Create an Account"}
          </h2>
          <p className="subtle" style={{ margin: 0 }}>
            {mode === "login"
              ? "Access your projects, model configurations, and generated code."
              : "Join Jinie to generate, customize, and build React Native apps."}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => {
              navigate("/login");
              setError("");
              setVerificationTicket("");
              setSuccess("");
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={mode === "signup" ? "active" : ""}
            onClick={() => {
              navigate("/signup");
              setError("");
              setVerificationTicket("");
              setSuccess("");
            }}
          >
            Create Account
          </button>
        </div>

        {error && <div className="auth-error-banner">{error}</div>}
        {notice && <p className="subtle" role="status">{notice}</p>}
        {verificationTicket ? <VerificationNotice apiBase={API} ticket={verificationTicket} onVerified={finishSession} /> : <GoogleSignIn apiBase={API} onSuccess={finishSession} onError={setError} disabled={loading} />}
        {verificationTicket && <button type="button" className="text-button" onClick={() => { setVerificationTicket(""); setNotice(""); setEmailOrUser(email || emailOrUser); navigate("/login"); }}>Back to sign in</button>}
        {success && (
          <div
            style={{
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              color: "#16a34a",
              padding: "10px 14px",
              borderRadius: 10,
              fontSize: 12,
              marginBottom: 12,
            }}
          >
            {success}
          </div>
        )}

        {!verificationTicket && (mode === "login" ? (
          <form onSubmit={handleLogin} className="auth-form">
<div className="auth-field">            <label className="field-label" htmlFor="login-cred">
              EMAIL ADDRESS
            </label>
            <input
              id="login-cred"
              type="text"
              required
              value={emailOrUser}
              onChange={(e) => setEmailOrUser(e.target.value)}
              placeholder="you@example.com"
              autoFocus
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="login-pwd">
              PASSWORD
            </label>
            <input
              id="login-pwd"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            /></div>

            <AuthRecovery apiBase={API} email={emailOrUser} password={password} onMessage={setNotice} onError={setError} onVerification={(ticket) => { setVerificationTicket(ticket); setNotice(""); }} />

            <button
              type="submit"
              className="primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? "Signing In…" : "Sign In ↗"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="auth-form auth-signup-form">
<div className="auth-field">            <label className="field-label" htmlFor="signup-fn">
              FULL NAME
            </label>
            <input
              id="signup-fn"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Sarah Connor"
              autoFocus
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-un">
              USERNAME
            </label>
            <input
              id="signup-un"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. sconnor"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-em">
              EMAIL ADDRESS
            </label>
            <input
              id="signup-em"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. sarah@example.com"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-pw">
              PASSWORD (MIN 8 CHARACTERS)
            </label>
            <input
              id="signup-pw"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a password"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-cpw">
              CONFIRM PASSWORD
            </label>
            <input
              id="signup-cpw"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
            /></div>

            <button
              type="submit"
              className="primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? "Creating Account…" : "Create Account ↗"}
            </button>
          </form>
        ))}

        <div style={{ textAlign: "center", marginTop: 18 }}>
          <Link
            to="/"
            className="text-button"
            style={{ fontSize: 11, color: "#7356da" }}
          >
            ← Back to Jinie Workspace
          </Link>
        </div>
      </div>
    </div>
  );
}
