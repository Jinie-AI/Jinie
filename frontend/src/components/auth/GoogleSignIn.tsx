import { authHeaders } from "../../modules/shared/studioApi";
import { apiErrorMessage } from "../../modules/shared/apiError";
import { useState } from "react";
import { initializeApp, getApps } from "firebase/app";
import { browserPopupRedirectResolver, GoogleAuthProvider, initializeAuth, inMemoryPersistence, signInWithPopup, signOut } from "firebase/auth";
import type { User } from "./AuthModal";
import "./auth-feedback.css";

const firebaseApp = getApps()[0] || initializeApp({
  apiKey: "AIzaSyAX1hCC3dScCA0NpkN_R95TNA4rF8qPRo4",
  authDomain: "jinie-web-app.firebaseapp.com",
  projectId: "jinie-web-app",
  appId: "1:552580434358:web:29e9997dc6b435f8dcd917",
});
const firebaseAuth = initializeAuth(firebaseApp, {
  persistence: inMemoryPersistence, popupRedirectResolver: browserPopupRedirectResolver,
});

export interface AuthSession { user: User; token: string; asset_token: string }

export default function GoogleSignIn({ apiBase, onSuccess, onError, disabled }: {
  apiBase: string; onSuccess: (session: AuthSession) => void;
  onError: (message: string) => void; disabled?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  async function login() {
    setBusy(true);
    onError("");
    try {
      const provider = new GoogleAuthProvider();
      provider.setCustomParameters({ prompt: "select_account" });
      const result = await signInWithPopup(firebaseAuth, provider);
      const idToken = await result.user.getIdToken();
      const response = await fetch(`${apiBase}/auth/firebase`, {
        method: "POST", headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });
      const session = await response.json();
      if (!response.ok) throw new Error(apiErrorMessage(session, "Google sign-in failed."));
      onSuccess(session);
    } catch (error) {
      const code = (error as { code?: string }).code;
      const messages: Record<string, string> = {
        "auth/operation-not-allowed": "Enable Google in Firebase Authentication → Sign-in method.",
        "auth/unauthorized-domain": "Add this website’s domain to Firebase Authentication → Settings → Authorized domains.",
        "auth/popup-blocked": "Allow popups for Jinie, then try Google sign-in again.",
        "auth/popup-closed-by-user": "Google sign-in was cancelled. You can try again.",
        "auth/account-exists-with-different-credential": "This email uses a different sign-in method. Sign in with that method first.",
      };
      onError(messages[code || ""] || (error instanceof Error ? error.message : "Google sign-in failed."));
    } finally {
      await signOut(firebaseAuth).catch(() => {});
      setBusy(false);
    }
  }
  return <>
    <button type="button" className="auth-google-button" disabled={busy || disabled} onClick={login}>
      <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="#4285F4" d="M21.6 12.23c0-.71-.06-1.39-.18-2.05H12v3.88h5.38a4.6 4.6 0 0 1-2 3.02v2.51h3.24c1.9-1.75 2.98-4.32 2.98-7.36Z"/>
        <path fill="#34A853" d="M12 22c2.7 0 4.96-.9 6.62-2.41l-3.24-2.51c-.9.6-2.05.97-3.38.97-2.6 0-4.8-1.76-5.59-4.12H3.07v2.59A10 10 0 0 0 12 22Z"/>
        <path fill="#FBBC05" d="M6.41 13.93a6 6 0 0 1 0-3.86V7.48H3.07a10 10 0 0 0 0 9.04l3.34-2.59Z"/>
        <path fill="#EA4335" d="M12 5.95c1.47 0 2.79.51 3.83 1.52l2.87-2.87A9.6 9.6 0 0 0 12 2a10 10 0 0 0-8.93 5.48l3.34 2.59C7.2 7.71 9.4 5.95 12 5.95Z"/>
      </svg>
      {busy ? "Connecting…" : "Continue with Google"}
    </button>
    <div className="auth-divider"><span>or use your email</span></div>
  </>;
}

