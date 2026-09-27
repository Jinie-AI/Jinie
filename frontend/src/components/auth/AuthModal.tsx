import { useState } from "react";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  initials: string;
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

  if (!isOpen) return null;

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!emailOrUser.trim() || !password) {
      setError("Please provide your username/email and password.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email_or_username: emailOrUser.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
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
    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName.trim(),
          username: username.trim(),
          email: email.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
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
          <span className="auth-logo-gem">✦</span>
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
            }}
          >
            Create Account
          </button>
        </div>

        {error && <div className="auth-error-banner">{error}</div>}

        {mode === "login" ? (
          <form onSubmit={handleLogin} className="auth-form">
            <label className="field-label" htmlFor="login-credential">
              EMAIL OR USERNAME
            </label>
            <input
              id="login-credential"
              type="text"
              required
              value={emailOrUser}
              onChange={(e) => setEmailOrUser(e.target.value)}
              placeholder="e.g. dev@jinie.ai or developer"
              autoFocus
            />

            <label className="field-label" htmlFor="login-password">
              PASSWORD
            </label>
            <input
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />

            <div className="auth-demo-hint">
              <small>
                Demo account: <code>dev@jinie.ai</code> /{" "}
                <code>password123</code>
              </small>
            </div>

            <button
              type="submit"
              className="primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? "Signing In…" : "Sign In to Workspace ↗"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="auth-form">
            <label className="field-label" htmlFor="signup-name">
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
            />

            <label className="field-label" htmlFor="signup-user">
              USERNAME
            </label>
            <input
              id="signup-user"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. sconnor"
            />

            <label className="field-label" htmlFor="signup-email">
              EMAIL ADDRESS
            </label>
            <input
              id="signup-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. sarah@example.com"
            />

            <label className="field-label" htmlFor="signup-pass">
              PASSWORD (MIN 6 CHARACTERS)
            </label>
            <input
              id="signup-pass"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a secure password"
            />

            <label className="field-label" htmlFor="signup-confirm">
              CONFIRM PASSWORD
            </label>
            <input
              id="signup-confirm"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
            />

            <button
              type="submit"
              className="primary auth-submit-btn"
              disabled={loading}
            >
              {loading ? "Creating Account…" : "Create Account & Sign In ↗"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
