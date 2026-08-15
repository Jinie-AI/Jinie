import { useState } from "react";

import type { DesignTokens } from "../design/DesignSection";
import type { GeneratedComponent } from "../generatedComponents/GeneratedComponentsSection";
import ScreenRenderer from "./ScreenRenderer";

interface PreviewSectionProps {
    srs?: any;
    designTokens?: DesignTokens | null;
    generatedComponents?: GeneratedComponent[];
    onDeploy: () => void;
}

type ViewTab = "preview" | "code";

export default function PreviewSection({
    designTokens,
    generatedComponents = [],
    onDeploy,
}: PreviewSectionProps) {
    const [activeScreenId, setActiveScreenId] = useState<string | null>(
        generatedComponents[0]?.screen_id ?? null
    );
    const [activeTab, setActiveTab] = useState<ViewTab>("preview");

    const activeComponent =
        generatedComponents.find((c) => c.screen_id === activeScreenId) ||
        generatedComponents[0] ||
        null;

    if (generatedComponents.length === 0) {
        return (
            <div className="section-card preview-panel">
                <div className="preview-panel__header">
                    <div>
                        <span className="stage-label">05 · Preview</span>
                        <h1>No screens to preview yet</h1>
                        <p>
                            Go back and generate your components first — this
                            stage renders whatever came out of that step.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="section-card preview-panel">
            <div className="preview-panel__header">
                <div>
                    <span className="stage-label">05 · Preview</span>
                    <h1>Your application is ready</h1>
                    <p>
                        {generatedComponents.length} screen
                        {generatedComponents.length !== 1 ? "s" : ""} generated
                        from your requirements and design choices. Review each
                        one below before deploying.
                    </p>
                </div>

                <span className="preview-ready-badge">
                    <span /> Ready to deploy
                </span>
            </div>

            <div className="design-layout-mode-row" style={{ flexWrap: "wrap" }}>
                {generatedComponents.map((component) => (
                    <button
                        key={component.screen_id}
                        type="button"
                        aria-pressed={activeComponent?.screen_id === component.screen_id}
                        onClick={() => setActiveScreenId(component.screen_id)}
                        className={
                            "chip-button" +
                            (activeComponent?.screen_id === component.screen_id
                                ? " chip-button--selected"
                                : "")
                        }
                    >
                        {component.screen_name}
                    </button>
                ))}
            </div>

            {activeComponent && (
                <>
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            flexWrap: "wrap",
                            gap: 8,
                            margin: "1rem 0 0.5rem",
                        }}
                    >
                        <strong>{activeComponent.component_name}</strong>

                        <div style={{ display: "flex", gap: 6 }}>
                            <button
                                type="button"
                                onClick={() => setActiveTab("preview")}
                                className={
                                    activeTab === "preview" ? "primary-button" : "secondary-button"
                                }
                            >
                                Preview
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveTab("code")}
                                className={
                                    activeTab === "code" ? "primary-button" : "secondary-button"
                                }
                            >
                                Code
                            </button>
                        </div>
                    </div>

                    {activeTab === "preview" ? (
                        <div className="app-preview" style={{ padding: "16px 0" }}>
                            <ScreenRenderer
                                layout={activeComponent.layout}
                                screenName={activeComponent.screen_name}
                                designTokens={designTokens}
                            />
                        </div>
                    ) : (
                        <div className="tech-stack-card">
                            <pre style={{ maxHeight: 420, overflow: "auto" }}>
                                <code>{activeComponent.code}</code>
                            </pre>
                        </div>
                    )}
                </>
            )}

            <div className="preview-actions">
                <div>
                    <strong>Everything looks good.</strong>
                    <span>Deploy your application whenever you are ready.</span>
                </div>

                <button className="primary-button" onClick={onDeploy}>
                    Deploy Application <span>→</span>
                </button>
            </div>
        </div>
    );
}
