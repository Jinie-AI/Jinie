import type { Design, Project } from "../shared/types";

interface Props {
  design: Design;
  recommendations: Project["recommendations"];
  onChange: (change: Partial<Design>) => void;
  disabled: boolean;
}

// Module 11 - Design Preferences: edits shared colours, typography, navigation and theme tokens.
export default function DesignControls({
  design,
  recommendations,
  onChange,
  disabled,
}: Props) {
  return (
    <fieldset className="screen-design-controls" disabled={disabled}>
      <legend>App appearance</legend>
      <p className="subtle">These choices apply across your screens.</p>
      <div className="screen-color-grid">
        {(
          [
            ["primary", "Primary", "#7c5ce0"],
            ["secondary", "Secondary", "#ede5f7"],
            ["accent", "Accent", "#b98849"],
          ] as const
        ).map(([key, label, fallback]) => (
          <label key={key}>
            {label}
            <input
              aria-label={label + " color"}
              type="color"
              value={design[key] || fallback}
              onChange={(event) => onChange({ [key]: event.target.value })}
            />
            <small>{design[key] || fallback}</small>
          </label>
        ))}
      </div>
      <label className="screen-field">
        Appearance
        <select
          value={design.theme}
          onChange={(event) => onChange({ theme: event.target.value })}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
      </label>
      <div className="screen-field-pair">
        <label className="screen-field">
          Headings
          <select
            value={design.font}
            onChange={(event) => onChange({ font: event.target.value })}
          >
            <option value="sans">Modern sans</option>
            <option value="serif">Editorial serif</option>
          </select>
        </label>
        <label className="screen-field">
          Body text
          <select
            value={design.bodyFont || "sans"}
            onChange={(event) => onChange({ bodyFont: event.target.value })}
          >
            <option value="sans">System sans</option>
            <option value="serif">System serif</option>
          </select>
        </label>
      </div>
      <label className="screen-field">
        Navigation
        <select
          value={design.navigation || "bottom"}
          onChange={(event) => onChange({ navigation: event.target.value })}
        >
          <option value="bottom">Bottom tabs</option>
          <option value="top">Top tabs</option>
          <option value="sidebar">Sidebar</option>
        </select>
      </label>
      <label className="screen-field">
        Default composition
        <select
          value={design.layout}
          onChange={(event) => onChange({ layout: event.target.value })}
        >
          <option value="grid">Grid</option>
          <option value="editorial">Editorial</option>
          <option value="cards">Horizontal cards</option>
        </select>
      </label>
      {recommendations.length > 0 && (
        <p className="subtle">
          Suggested compositions:{" "}
          {recommendations.map((item) => item.id).join(" · ")}. You can override
          the layout for each screen below.
        </p>
      )}
    </fieldset>
  );
}
