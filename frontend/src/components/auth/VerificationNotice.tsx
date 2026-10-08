import { authHeaders } from "../../modules/shared/studioApi";
import { apiErrorMessage } from "../../modules/shared/apiError";
import { useEffect, useRef, useState } from "react";
import type { AuthSession } from "./GoogleSignIn";
import "./auth-feedback.css";

export default function VerificationNotice({ apiBase, ticket, onVerified }: {
  apiBase: string; ticket: string; onVerified: (session: AuthSession) => void;
}) {
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState("");
  const callback = useRef(onVerified);
  useEffect(() => { callback.current = onVerified; }, [onVerified]);
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    const controller = new AbortController();
    async function check() {
      try {
        const response = await fetch(`${apiBase}/auth/verification-status`, {
          method: "POST", headers: { ...authHeaders(), "Content-Type": "application/json" },
          body: JSON.stringify({ ticket }), signal: controller.signal,
        });
        const data = await response.json();
        if (cancelled) return;
        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            setError(apiErrorMessage(data, "Sign in to check your verification."));
            return;
          }
          throw new Error("Connection interrupted. Checking again…");
        }
        setError("");
        if (data.verified) {
          setVerified(true);
          timer = setTimeout(() => { if (!cancelled) callback.current(data); }, 1500);
          return;
        }
      } catch {
        if (cancelled) return;
        setError("Waiting for a connection. Checking again…");
      }
      if (!cancelled) timer = setTimeout(check, 5000);
    }
    timer = setTimeout(check, 1500);
    return () => { cancelled = true; clearTimeout(timer); controller.abort(); };
  }, [apiBase, ticket]);
  return <div className={`auth-verification-box ${verified ? "is-verified" : ""}`} role="status" aria-live="polite">
    <span className="auth-verification-icon" aria-hidden="true">{verified ? "✓" : "✉"}</span>
    <div><strong>{verified ? "Verified Successfully" : "Verification Link sent"}</strong>
      <p>{verified ? "Opening your workspace…" : "Open the link in your email. This box updates automatically."}</p>
      {error && <p>{error}</p>}
    </div>
  </div>;
}

