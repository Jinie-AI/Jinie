export const API =
  (
    import.meta.env.VITE_API_URL ||
    (typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
      ? ""
      : "http://127.0.0.1:8000")
  ).replace(/\/$/, "") + "/api";
export async function request<T>(
  path: string,
  method = "GET",
  data?: unknown,
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(
    () => controller.abort(),
    method === "GET" ? 20000 : 120000,
  );
  try {
    if (path !== "/health" && !path.startsWith("/auth/") && !localStorage.getItem("jinie_auth_token")) await ensureGuest();
    const response = await fetch(API + path, {
      signal: controller.signal,
      method,
      headers: { ...authHeaders(), ...(data ? { "Content-Type": "application/json" } : {}) },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!response.ok) {
      let message: string;
      try {
        const body = await response.json();
        message =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      } catch {
        message = response.statusText;
      }
      if (response.status === 403 && message.includes("2 free prompts")) {
        window.dispatchEvent(new CustomEvent("jinie-login-required", { detail: message }));
      }
      throw new Error(message);
    }
    return await response.json();
  } catch (error) {
    if (controller.signal.aborted)
      throw new Error(
        "The server took too long to respond. Check recent projects before trying again; the server may still finish saving your request.",
      );
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("jinie_auth_token");
  const guest = localStorage.getItem("jinie_guest_token");
  return { ...(token ? { Authorization: "Bearer " + token } : {}), ...(guest ? { "X-Jinie-Guest": guest } : {}) };
}

let guestPending: Promise<{ remaining: number }> | undefined;
export async function ensureGuest(refresh = false): Promise<{ remaining: number }> {
  if (!refresh && localStorage.getItem("jinie_guest_token")) return { remaining: Number(localStorage.getItem("jinie_guest_remaining") ?? 2) };
  if (!guestPending) guestPending = (async () => {
    const response = await fetch(API + "/auth/guest", { method: "POST", headers: authHeaders() });
    const session = await response.json();
    if (!response.ok) throw new Error(session.detail || "Could not start a guest session.");
    localStorage.setItem("jinie_guest_token", session.guest_token);
    localStorage.setItem("jinie_guest_asset_token", session.asset_token);
    localStorage.setItem("jinie_guest_remaining", String(session.remaining));
    return session;
  })().finally(() => { guestPending = undefined; });
  return guestPending;
}

export function previewAssetToken(): string {
  return localStorage.getItem(localStorage.getItem("jinie_auth_token") ? "jinie_asset_token" : "jinie_guest_asset_token") || "";
}

// Read-only access tokens allow sandboxed previews and downloads without exposing a workspace login token.
export function assetUrl(url: string): string {
  const token = previewAssetToken();
  if (!token) return url;
  if (url.includes("/preview/")) return url.replace("/preview/", "/preview/~" + encodeURIComponent(token) + "/");
  return url + (url.includes("?") ? "&" : "?") + "asset_token=" + encodeURIComponent(token);
}
export const samples = [
  {
    name: "The Everyday Edit",
    text: "Build a minimal clothing boutique with home, products, product detail, cart, checkout, search, about and contact pages.",
  },
  {
    name: "Crave Kitchen",
    text: "Mujhe food restaurant ki app chahiye. Menu products, cart, checkout cash on delivery, search aur contact page ho. Playful design.",
  },
  {
    name: "Forma Living",
    text: "Create a luxury furniture shop with a home page, catalog, product details, cart, checkout and contact.",
  },
];
export const pages = [
  "home",
  "products",
  "detail",
  "cart",
  "checkout",
  "contact",
  "about",
  "search",
  "settings",
  "profile",
];
export const tabs = [
  "Prompt",
  "Requirements",
  "Screens",
  "Preview",
  "Code",
  "Evidence",
  "Deploy",
];
