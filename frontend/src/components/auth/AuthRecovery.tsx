import { useState } from "react";

// Firebase sends recovery links; Jinie never creates verification codes or stores account passwords.
export default function AuthRecovery({ apiBase, email, password, onMessage, onError, onVerification }: {
  apiBase: string; email: string; password: string;
  onMessage: (message: string) => void; onError: (message: string) => void;
  onVerification?: (ticket: string) => void;
}) {
  const [busy, setBusy] = useState(false);
  async function send(kind: "reset-password" | "resend-verification") {
    if (!email.trim() || (kind === "resend-verification" && !password)) {
      onError(kind === "reset-password" ? "Enter your email address first." : "Enter your email and password first.");
      return;
    }
    setBusy(true);
    onError("");
    try {
      const response = await fetch(`${apiBase}/auth/${kind}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(kind === "reset-password" ? { email: email.trim() } : { email_or_username: email.trim(), password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not send the email.");
      onMessage(data.message);
      if (data.verification_ticket) onVerification?.(data.verification_ticket);
    } catch (error) {
      onError(error instanceof Error ? error.message : "Could not send the email.");
    } finally { setBusy(false); }
  }
  return <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
    <button type="button" className="text-button" disabled={busy} onClick={() => send("reset-password")}>Forgot password?</button>
    <button type="button" className="text-button" disabled={busy} onClick={() => send("resend-verification")}>Resend verification</button>
  </div>;
}
