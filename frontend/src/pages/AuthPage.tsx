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
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();
  const location = useLocation();

  const mode =
    location.pathname === "/signup"
      ? "signup"
      : location.pathname === "/login"
        ? "login"
        : defaultMode;

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!emailOrUser.trim() || !password) {
      setError("Please provide your username/email and password.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email_or_username: emailOrUser.trim(),
          password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
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
      const res = await fetch(`${API}/auth/signup`, {
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
              setSuccess("");
            }}
          >
            Create Account
          </button>
        </div>

        {error && <div className="auth-error-banner">{error}</div>}
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

        {mode === "login" ? (
          <form onSubmit={handleLogin} className="auth-form">
            <label className="field-label" htmlFor="login-cred">
              EMAIL OR USERNAME
            </label>
            <input
              id="login-cred"
              type="text"
              required
              value={emailOrUser}
              onChange={(e) => setEmailOrUser(e.target.value)}
              placeholder="e.g. dev@jinie.ai or developer"
              autoFocus
            />

            <label className="field-label" htmlFor="login-pwd">
              PASSWORD
            </label>
            <input
              id="login-pwd"
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
              {loading ? "Signing In…" : "Sign In ↗"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="auth-form">
            <label className="field-label" htmlFor="signup-fn">
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
            />

            <label className="field-label" htmlFor="signup-un">
              USERNAME
            </label>
            <input
              id="signup-un"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. sconnor"
            />

            <label className="field-label" htmlFor="signup-em">
              EMAIL ADDRESS
            </label>
            <input
              id="signup-em"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. sarah@example.com"
            />

            <label className="field-label" htmlFor="signup-pw">
              PASSWORD (MIN 6 CHARACTERS)
            </label>
            <input
              id="signup-pw"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a password"
            />

            <label className="field-label" htmlFor="signup-cpw">
              CONFIRM PASSWORD
            </label>
            <input
              id="signup-cpw"
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
              {loading ? "Creating Account…" : "Create Account ↗"}
            </button>
          </form>
        )}

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
