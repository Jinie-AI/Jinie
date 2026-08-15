import { useEffect, useRef, useState } from "react";

import { generateComponents } from "../../services/JinieService";
import type { DesignTokens } from "../design/DesignSection";

export interface GeneratedComponent {
    screen_id: string;
    screen_name: string;
    component_name: string;
    code: string;
    layout: Record<string, any>;
}

interface GeneratedComponentsSectionProps {
    srs: any;
    designTokens: DesignTokens;
    onApprove: (components: GeneratedComponent[]) => void;
}

/**
 * Maps the simple DesignTokens the Design Preferences Panel collects
 * into the richer design_tokens shape ComponentGenerator's rule-based
 * fallback renderer reads from (colors.surface / colors.onPrimary,
 * typography.fontSize, spacing.default, borderRadius). The AI-first
 * path just forwards this object as-is to the LLM, so extra fields
 * here are harmless either way — they just make the fallback path
 * actually reflect what the user picked instead of falling back to
 * its own hardcoded defaults.
 */
function toGeneratorDesignTokens(tokens: DesignTokens) {
    return {
        colors: {
            primary: tokens.colors.primary,
            secondary: tokens.colors.secondary,
            accent: tokens.colors.accent,
            surface: tokens.theme === "dark" ? "#0F172A" : "#FFFFFF",
            onPrimary: "#FFFFFF",
        },
        typography: {
            headingFont: tokens.typography.headingFont,
            bodyFont: tokens.typography.bodyFont,
            fontSize: 14,
            fontWeight: "500",
        },
        spacing: { default: 8 },
        borderRadius: 12,
        layoutMode: tokens.layoutMode,
        theme: tokens.theme,
    };
}

export default function GeneratedComponentsSection({
    srs,
    designTokens,
    onApprove,
}: GeneratedComponentsSectionProps) {
    const [status, setStatus] = useState<"loading" | "error" | "done">("loading");
    const [errorMessage, setErrorMessage] = useState<string>("");
    const [components, setComponents] = useState<GeneratedComponent[]>([]);
    const [failed, setFailed] = useState<Array<{ screen_name: string; error: string }>>([]);
    const [activeIndex, setActiveIndex] = useState(0);
    const [copied, setCopied] = useState(false);

    // React.StrictMode intentionally double-invokes effects in
    // development to surface side-effect bugs. Without this guard,
    // that means every real backend call here — including the Groq
    // API calls it triggers — fires twice per mount, which both
    // wastes free-tier quota and can trip rate limits unnecessarily.
    const hasStartedGeneration = useRef(false);

    const runGeneration = () => {
        setStatus("loading");
        setErrorMessage("");
        setCopied(false);

        generateComponents(
            srs?.component_trees,
            toGeneratorDesignTokens(designTokens),
            srs?.tech_stack,
            srs?.trace_id
        )
            .then((result) => {
                console.log("FULL GENERATE COMPONENTS RESULT:", result);
                console.log("COMPONENTS:", result.components);
                console.log("FIRST COMPONENT:", result.components?.[0]);
                console.log("FIRST COMPONENT LAYOUT:", result.components?.[0]?.layout);

                setComponents(result.components ?? []);
                setFailed(result.failed ?? []);
                setActiveIndex(0);
                setStatus("done");
            })
            .catch((error: Error) => {
                setErrorMessage(error.message || "Component generation failed.");
                setStatus("error");
            });
    };

    // Fire automatically once, when this stage first mounts with a
    // real srs.component_trees payload in hand.
    useEffect(() => {
        if (hasStartedGeneration.current) return;
        hasStartedGeneration.current = true;
        runGeneration();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);


    const activeComponent = components[activeIndex];

    const handleCopy = async () => {
        if (!activeComponent) return;
        try {
            await navigator.clipboard.writeText(activeComponent.code);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
        } catch {
            // Clipboard API can fail silently in some contexts (e.g. no
            // permission, non-HTTPS) — not worth surfacing as an error.
        }
    };

    if (status === "loading") {
        return (
            <div className="section-card">
                <span className="stage-label">04 · Components</span>
                <h1>Generating your components…</h1>
                <p>
                    Sending {srs?.component_trees?.trees?.length ?? 0} screen
                    {(srs?.component_trees?.trees?.length ?? 0) === 1 ? "" : "s"} and your chosen
                    design tokens to the Component Generator.
                </p>
            </div>
        );
    }

    if (status === "error") {
        return (
            <div className="section-card">
                <span className="stage-label">04 · Components</span>
                <h1>Component generation failed</h1>
                <p className="empty-srs">{errorMessage}</p>
                <div className="srs-actions">
                    <button className="primary-button" type="button" onClick={runGeneration}>
                        Retry <span>↻</span>
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="section-card">
            <div className="design-panel__header">
                <div>
                    <span className="stage-label">04 · Components</span>
                    <h1>Generated Components</h1>
                    <p>
                        {components.length} component{components.length === 1 ? "" : "s"} generated
                        from your requirements and design choices.
                        {failed.length > 0 && (
                            <> {failed.length} screen{failed.length === 1 ? "" : "s"} failed — see below.</>
                        )}
                    </p>
                </div>
            </div>

            {components.length > 0 && (
                <>
                    <div className="design-layout-mode-row" style={{ flexWrap: "wrap" }}>
                        {components.map((component, index) => (
                            <button
                                key={component.screen_id}
                                type="button"
                                aria-pressed={activeIndex === index}
                                onClick={() => setActiveIndex(index)}
                                className={
                                    "chip-button" +
                                    (activeIndex === index ? " chip-button--selected" : "")
                                }
                            >
                                {component.component_name}
                            </button>
                        ))}
                    </div>

                    {activeComponent && (
                        <div className="tech-stack-card">
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    marginBottom: "0.5rem",
                                }}
                            >
                                <strong>{activeComponent.component_name}.tsx</strong>
                                <button className="secondary-button" type="button" onClick={handleCopy}>
                                    {copied ? "Copied" : "Copy code"}
                                </button>
                            </div>
                            <pre style={{ maxHeight: 420, overflow: "auto" }}>
                                <code>{activeComponent.code}</code>
                            </pre>
                        </div>
                    )}
                </>
            )}

            {failed.length > 0 && (
                <div className="srs-block">
                    <h2>Failed screens</h2>
                    <div className="srs-list">
                        {failed.map((failure) => (
                            <div className="srs-item" key={failure.screen_name}>
                                <span className="srs-number">✕</span>
                                <span>
                                    {failure.screen_name}: {failure.error}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="design-actions">
                <div>
                    <strong>Components look right?</strong>
                    <span>Continue to the interactive preview.</span>
                </div>
                <button
                    className="primary-button"
                    type="button"
                    disabled={components.length === 0}
                    onClick={() => onApprove(components)}
                >
                    Continue to Preview <span>→</span>
                </button>
            </div>
        </div>
    );
}
