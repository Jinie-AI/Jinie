// FastAPI validation errors can contain arrays of field errors, not just text.
export function apiErrorMessage(value: unknown, fallback: string): string {
  if (typeof value === "string") return value.trim() || fallback;
  if (Array.isArray(value)) {
    const messages = value.map((item) => apiErrorMessage(item, "")).filter(Boolean);
    return [...new Set(messages)].join("\n") || fallback;
  }
  if (value && typeof value === "object") {
    const error = value as Record<string, unknown>;
    if (typeof error.msg === "string") {
      if (error.type === "string_pattern_mismatch" && Array.isArray(error.loc) && error.loc.at(-1) === "username") {
        return "Username cannot have space";
      }
      const field = Array.isArray(error.loc)
        ? error.loc.filter((part) => typeof part === "string" && !["body", "query", "path"].includes(part)).join(" ").replaceAll("_", " ")
        : "";
      return field ? `${field.charAt(0).toUpperCase()}${field.slice(1)}: ${error.msg}` : error.msg;
    }
    for (const key of ["detail", "message", "error"]) {
      const message = apiErrorMessage(error[key], "");
      if (message) return message;
    }
  }
  return fallback;
}
