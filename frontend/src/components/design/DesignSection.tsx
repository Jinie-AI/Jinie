import { useState } from "react";

export interface DesignTokens {
    colors: {
        primary: string;
        secondary: string;
        accent: string;
    };
    typography: {
        headingFont: string;
        bodyFont: string;
    };
    layoutMode: "top-nav" | "side-nav" | "drawer";
    theme: "light" | "dark" | "system";
}

interface DesignSectionProps {
    srs: any;
    onApprove: (designTokens: DesignTokens) => void;
}

const COLOR_PRESETS: Array<{ name: string; primary: string; secondary: string; accent: string }> = [
    { name: "Ocean", primary: "#2563EB", secondary: "#1E3A8A", accent: "#38BDF8" },
    { name: "Sunset", primary: "#EA580C", secondary: "#7C2D12", accent: "#FACC15" },
    { name: "Orchid", primary: "#9333EA", secondary: "#4C1D95", accent: "#F472B6" },
    { name: "Forest", primary: "#15803D", secondary: "#14532D", accent: "#84CC16" },
    { name: "Slate", primary: "#334155", secondary: "#0F172A", accent: "#94A3B8" },
];

const FONT_OPTIONS = ["Inter", "Poppins", "Roboto", "Source Serif 4", "Space Grotesk"];

const LAYOUT_MODES: Array<{ value: DesignTokens["layoutMode"]; label: string }> = [
    { value: "top-nav", label: "Top Nav" },
    { value: "side-nav", label: "Side Nav" },
    { value: "drawer", label: "Drawer" },
];

export default function DesignSection({ srs, onApprove }: DesignSectionProps) {
    const [selectedPreset, setSelectedPreset] = useState(0);
    const [headingFont, setHeadingFont] = useState(FONT_OPTIONS[0]);
    const [bodyFont, setBodyFont] = useState(FONT_OPTIONS[1]);
    const [layoutMode, setLayoutMode] = useState<DesignTokens["layoutMode"]>("top-nav");
    const [theme, setTheme] = useState<DesignTokens["theme"]>("light");

    const activePreset = COLOR_PRESETS[selectedPreset];
    const screenCount = srs?.sitemap?.nodes?.length ?? 0;

    const handleApprove = () => {
        const designTokens: DesignTokens = {
            colors: {
                primary: activePreset.primary,
                secondary: activePreset.secondary,
                accent: activePreset.accent,
            },
            typography: {
                headingFont,
                bodyFont,
            },
            layoutMode,
            theme,
        };
        onApprove(designTokens);
    };

    return (
        <div className="section-card design-panel">
            <div className="design-panel__header">
                <div>
                    <span className="stage-label">03 · Design</span>
                    <h1>Application Design</h1>
                    <p>
                        Choose how your {screenCount || ""} generated screen
                        {screenCount === 1 ? "" : "s"} should look and feel.
                    </p>
                </div>

                <div className="design-panel__status">
                    <span className="design-panel__status-dot" />
                    Design ready
                </div>
            </div>

            <div className="design-layout">
                <div className="design-sidebar">
                    <span className="design-sidebar__label">Color palette</span>
                    <div className="design-color-row">
                        {COLOR_PRESETS.map((preset, index) => (
                            <button
                                key={preset.name}
                                type="button"
                                title={preset.name}
                                aria-pressed={selectedPreset === index}
                                onClick={() => setSelectedPreset(index)}
                                className={
                                    "color-swatch-button" +
                                    (selectedPreset === index ? " color-swatch-button--selected" : "")
                                }
                                style={{ backgroundColor: preset.primary }}
                            />
                        ))}
                    </div>
                    <div className="design-detail">
                        <span>Palette</span>
                        <strong>{activePreset.name}</strong>
                    </div>

                    <span className="design-sidebar__label">Typography</span>
                    <div className="design-detail design-detail--stacked">
                        <label>
                            Heading font
                            <select
                                value={headingFont}
                                onChange={(e) => setHeadingFont(e.target.value)}
                            >
                                {FONT_OPTIONS.map((font) => (
                                    <option key={font} value={font}>
                                        {font}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label>
                            Body font
                            <select
                                value={bodyFont}
                                onChange={(e) => setBodyFont(e.target.value)}
                            >
                                {FONT_OPTIONS.map((font) => (
                                    <option key={font} value={font}>
                                        {font}
                                    </option>
                                ))}
                            </select>
                        </label>
                    </div>

                    <span className="design-sidebar__label">Layout mode</span>
                    <div className="design-layout-mode-row">
                        {LAYOUT_MODES.map((mode) => (
                            <button
                                key={mode.value}
                                type="button"
                                aria-pressed={layoutMode === mode.value}
                                onClick={() => setLayoutMode(mode.value)}
                                className={
                                    "chip-button" +
                                    (layoutMode === mode.value ? " chip-button--selected" : "")
                                }
                            >
                                {mode.label}
                            </button>
                        ))}
                    </div>

                    <span className="design-sidebar__label">Theme</span>
                    <div className="design-layout-mode-row">
                        {(["light", "dark", "system"] as const).map((option) => (
                            <button
                                key={option}
                                type="button"
                                aria-pressed={theme === option}
                                onClick={() => setTheme(option)}
                                className={
                                    "chip-button" +
                                    (theme === option ? " chip-button--selected" : "")
                                }
                            >
                                {option[0].toUpperCase() + option.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="design-preview">
                    <div
                        className="mock-screen"
                        style={{
                            backgroundColor: theme === "dark" ? "#0F172A" : "#FFFFFF",
                            color: theme === "dark" ? "#F8FAFC" : "#0F172A",
                        }}
                    >
                        <div
                            className="mock-header"
                            style={{ backgroundColor: activePreset.primary, color: "#FFFFFF" }}
                        >
                            <div className="mock-logo">J</div>
                            <span style={{ fontFamily: headingFont }}>Your App</span>
                            <div className="mock-avatar" />
                        </div>

                        <div className="mock-content">
                            <span
                                className="mock-eyebrow"
                                style={{ color: activePreset.accent }}
                            >
                                WELCOME BACK
                            </span>
                            <h3 style={{ fontFamily: headingFont }}>
                                Everything in one place.
                            </h3>
                            <p style={{ fontFamily: bodyFont, fontSize: "0.85rem" }}>
                                {screenCount > 0
                                    ? `${screenCount} screens generated from your requirements.`
                                    : "Your generated screens will appear here."}
                            </p>

                            <div className="mock-card">
                                <div
                                    className="mock-card__icon"
                                    style={{ color: activePreset.secondary }}
                                >
                                    ✦
                                </div>
                                <div>
                                    <strong style={{ fontFamily: headingFont }}>
                                        Recent activity
                                    </strong>
                                    <span style={{ fontFamily: bodyFont }}>
                                        Your project is ready to review
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="design-actions">
                <div>
                    <strong>Happy with the direction?</strong>
                    <span>You can continue to the interactive preview.</span>
                </div>

                <button className="primary-button" onClick={handleApprove}>
                    Approve Design <span>→</span>
                </button>
            </div>
        </div>
    );
}
