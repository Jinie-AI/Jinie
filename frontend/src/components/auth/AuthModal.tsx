import { authHeaders } from "../../modules/shared/studioApi";
import GoogleSignIn, { type AuthSession } from "./GoogleSignIn";
import VerificationNotice from "./VerificationNotice";
import AuthRecovery from "./AuthRecovery";
import BrandLogo from "../BrandLogo";
import { useEffect, useState } from "react";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  initials: string;
  email_verified?: boolean;
  photo_url?: string;
  sign_in_methods?: string[];
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: User, token: string) => void;
  apiBase: string;
}

export default function AuthModal({
  isOpen,
  onClose,
  onAuthSuccess,
  apiBase,
}: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
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
  useEffect(() => {
    if (!isOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = previous; };
  }, [isOpen]);

  if (!isOpen) return null;

  function finishSession(session: AuthSession) {
    localStorage.setItem("jinie_asset_token", session.asset_token || "");
    setVerificationTicket("");
    onAuthSuccess(session.user, session.token);
    onClose();
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
      const res = await fetch(`${apiBase}/auth/login`, {
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
      onAuthSuccess(data.user, data.token);
      onClose();
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
      const res = await fetch(`${apiBase}/auth/signup`, {
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
      onAuthSuccess(data.user, data.token);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="auth-modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
        <button
          className="auth-modal-close"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>

        <div className="auth-modal-header">
          <BrandLogo />
          <h2>{mode === "login" ? "Welcome Back" : "Create an Account"}</h2>
          <p className="subtle">
            {mode === "login"
              ? "Sign in to access your projects and personalized workspace."
              : "Join Jinie to generate, customize and export native mobile applications."}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => {
              setMode("login");
              setError("");
              setVerificationTicket("");
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={mode === "signup" ? "active" : ""}
            onClick={() => {
              setMode("signup");
              setError("");
              setVerificationTicket("");
            }}
          >
            Create Account
          </button>
        </div>

        {error && <div className="auth-error-banner">{error}</div>}
        {notice && <p className="subtle" role="status">{notice}</p>}
        {verificationTicket ? <VerificationNotice apiBase={apiBase} ticket={verificationTicket} onVerified={finishSession} /> : <GoogleSignIn apiBase={apiBase} onSuccess={finishSession} onError={setError} disabled={loading} />}
        {verificationTicket && <button type="button" className="text-button" onClick={() => { setVerificationTicket(""); setNotice(""); setMode("login"); setEmailOrUser(email || emailOrUser); }}>Back to sign in</button>}

        {!verificationTicket && (mode === "login" ? (
          <form onSubmit={handleLogin} className="auth-form">
<div className="auth-field">            <label className="field-label" htmlFor="login-credential">
              EMAIL ADDRESS
            </label>
            <input
              id="login-credential"
              type="text"
              required
              value={emailOrUser}
              onChange={(e) => setEmailOrUser(e.target.value)}
              placeholder="you@example.com"
              autoFocus
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="login-password">
              PASSWORD
            </label>
            <input
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            /></div>

            <AuthRecovery apiBase={apiBase} email={emailOrUser} password={password} onMessage={setNotice} onError={setError} onVerification={(ticket) => { setVerificationTicket(ticket); setNotice(""); }} />

            <button
              type="submit"
              className="primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? "Signing In…" : "Sign In to Workspace ↗"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="auth-form auth-signup-form">
<div className="auth-field">            <label className="field-label" htmlFor="signup-name">
              FULL NAME
            </label>
            <input
              id="signup-name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Sarah Connor"
              autoFocus
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-user">
              USERNAME
            </label>
            <input
              id="signup-user"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. sconnor"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-email">
              EMAIL ADDRESS
            </label>
            <input
              id="signup-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. sarah@example.com"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-pass">
              PASSWORD (MIN 8 CHARACTERS)
            </label>
            <input
              id="signup-pass"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a secure password"
            /></div>

<div className="auth-field">            <label className="field-label" htmlFor="signup-confirm">
              CONFIRM PASSWORD
            </label>
            <input
              id="signup-confirm"
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
      </div>
    </div>
  );
}
