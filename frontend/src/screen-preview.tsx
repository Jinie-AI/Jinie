import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import AppView from "../../backend/studio/templates/AppView.jsx";
export function Screen() {
  const [value, setValue] = useState<{
    config: Record<string, unknown>;
    page: string;
  } | null>(null);
  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (
        event.source === parent &&
        event.origin === location.origin &&
        event.data?.type === "jinie-screen-config"
      )
        setValue(event.data);
    };
    window.addEventListener("message", receive);
    parent.postMessage({ type: "jinie-screen-ready" }, location.origin);
    return () => window.removeEventListener("message", receive);
  }, []);
  return value ? (
    <AppView
      key={value.page}
      config={value.config}
      initialScreen={value.page}
    />
  ) : null;
}
createRoot(document.getElementById("root")!).render(<Screen />);
