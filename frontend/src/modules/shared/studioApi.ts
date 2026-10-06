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
    const response = await fetch(API + path, {
      signal: controller.signal,
      method,
      headers: data ? { "Content-Type": "application/json" } : {},
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
