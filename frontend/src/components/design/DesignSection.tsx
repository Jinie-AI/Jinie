import { useState } from "react";

export interface DesignTokens {
    colors: {
        primary: string;
        secondary: string;
        accent: string;
    };
    // True when the user explicitly picked these exact colors themselves
    // (rather than choosing one of the built-in presets). Carried through
    // to the backend so the AI generation prompt can treat these as a
    // hard requirement instead of a soft suggestion.
    isCustomColor: boolean;
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
    const [colorMode, setColorMode] = useState<"preset" | "custom">("preset");
    // Shown immediately when this step loads, before the user can see or
    // touch anything else — forces an explicit choice up front instead of
    // burying "choose your own colors" as a toggle the user might never
    // scroll down far enough to notice.
    const [showColorModal, setShowColorModal] = useState(true);
    const [selectedPreset, setSelectedPreset] = useState(0);
    const [customColors, setCustomColors] = useState({
        primary: "#2563EB",
        secondary: "#1E3A8A",
        accent: "#38BDF8",
    });
    const [headingFont, setHeadingFont] = useState(FONT_OPTIONS[0]);
    const [bodyFont, setBodyFont] = useState(FONT_OPTIONS[1]);
    const [layoutMode, setLayoutMode] = useState<DesignTokens["layoutMode"]>("top-nav");
    const [theme, setTheme] = useState<DesignTokens["theme"]>("light");

    const activePreset = COLOR_PRESETS[selectedPreset];
    // Whichever mode is active, this is the single source of truth the
    // rest of the component (preview + approve) reads colors from.
    const activeColors = colorMode === "custom" ? customColors : activePreset;
    const screenCount = srs?.sitemap?.nodes?.length ?? 0;

    const handleApprove = () => {
        const designTokens: DesignTokens = {
            colors: {
                primary: activeColors.primary,
                secondary: activeColors.secondary,
                accent: activeColors.accent,
            },
            isCustomColor: colorMode === "custom",
            typography: {
                headingFont,
                bodyFont,
            },
            layoutMode,
            theme,
        };
        onApprove(designTokens);
    };

    const handleChooseModalOption = (mode: "preset" | "custom") => {
        setColorMode(mode);
        setShowColorModal(false);
    };

    return (
        <div className="section-card design-panel">
            {showColorModal && (
                <div className="color-modal-backdrop">
                    <div className="color-modal" role="dialog" aria-modal="true">
                        <span className="stage-label">Before you continue</span>
                        <h2>How should we pick your app's colors?</h2>
                        <p>
                            You can go with a ready-made palette, or choose the
                            exact colors yourself — either way, this only takes
                            a second.
                        </p>

                        <div className="color-modal-options">
                            <button
                                type="button"
                                className="color-modal-option"
                                onClick={() => handleChooseModalOption("preset")}
                            >
                                <span className="color-modal-option__swatches">
                                    {COLOR_PRESETS.slice(0, 3).map((preset) => (
                                        <span
                                            key={preset.name}
                                            style={{ backgroundColor: preset.primary }}
                                        />
                                    ))}
                                </span>
                                <strong>Use a preset</strong>
                                <span>Pick from curated color palettes</span>
                            </button>

                            <button
                                type="button"
                                className="color-modal-option"
                                onClick={() => handleChooseModalOption("custom")}
                            >
                                <span className="color-modal-option__swatches color-modal-option__swatches--custom">
                                    🎨
                                </span>
                                <strong>Choose my own</strong>
                                <span>Pick your exact brand colors</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

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
                    <div className="design-layout-mode-row">
                        <button
                            type="button"
                            aria-pressed={colorMode === "preset"}
                            onClick={() => setColorMode("preset")}
                            className={
                                "chip-button" +
                                (colorMode === "preset" ? " chip-button--selected" : "")
                            }
                        >
                            Use a preset
                        </button>
                        <button
                            type="button"
                            aria-pressed={colorMode === "custom"}
                            onClick={() => setColorMode("custom")}
                            className={
                                "chip-button" +
                                (colorMode === "custom" ? " chip-button--selected" : "")
                            }
                        >
                            Choose my own
                        </button>
                    </div>

                    {colorMode === "preset" ? (
                        <>
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
                        </>
                    ) : (
                        <div className="design-detail design-detail--stacked">
                            <label>
                                Primary color
                                <input
                                    type="color"
                                    className="color-input"
                                    value={customColors.primary}
                                    onChange={(e) =>
                                        setCustomColors((prev) => ({ ...prev, primary: e.target.value }))
                                    }
                                />
                            </label>
                            <label>
                                Secondary color
                                <input
                                    type="color"
                                    className="color-input"
                                    value={customColors.secondary}
                                    onChange={(e) =>
                                        setCustomColors((prev) => ({ ...prev, secondary: e.target.value }))
                                    }
                                />
                            </label>
                            <label>
                                Accent color
                                <input
                                    type="color"
                                    className="color-input"
                                    value={customColors.accent}
                                    onChange={(e) =>
                                        setCustomColors((prev) => ({ ...prev, accent: e.target.value }))
                                    }
                                />
                            </label>
                        </div>
                    )}

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
                            style={{ backgroundColor: activeColors.primary, color: "#FFFFFF" }}
                        >
                            <div className="mock-logo">J</div>
                            <span style={{ fontFamily: headingFont }}>Your App</span>
                            <div className="mock-avatar" />
                        </div>

                        <div className="mock-content">
                            <span
                                className="mock-eyebrow"
                                style={{ color: activeColors.accent }}
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
                                    style={{ color: activeColors.secondary }}
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
