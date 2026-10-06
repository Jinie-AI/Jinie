declare module "*AppView.jsx" {
  import type { ComponentType } from "react";
  const AppView: ComponentType<{
    config: Record<string, unknown>;
    initialScreen?: string;
  }>;
  export default AppView;
}
