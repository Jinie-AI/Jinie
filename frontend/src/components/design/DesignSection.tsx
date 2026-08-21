import { useState } from "react";

export interface DesignTokens {
    colors: {
        primary: string;
        secondary: string;
        accent: string;
    };
    isCustomColor: boolean;
    typography: {
        headingFont: string;
        bodyFont: string;
    };
    layoutMode: "top-nav" | "side-nav" | "drawer";
    theme: "light" | "dark" | "system";
}

interface DesignSectionProps {
    srs?: any;
    onApprove: (designTokens: DesignTokens) => void;
}

const COLOR_PRESETS: Array<{ name: string; primary: string; secondary: string; accent: string }> = [
    { name: "Ocean", primary: "#2563EB", secondary: "#1E3A8A", accent: "#38BDF8" },
    { name: "Bittersweet", primary: "#FF6B6B", secondary: "#39605D", accent: "#FFE66D" },
    { name: "Sunset", primary: "#EA580C", secondary: "#7C2D12", accent: "#FACC15" },
    { name: "Orchid", primary: "#9333EA", secondary: "#4C1D95", accent: "#F472B6" },
    { name: "Forest", primary: "#15803D", secondary: "#14532D", accent: "#84CC16" },
    { name: "Slate", primary: "#334155", secondary: "#0F172A", accent: "#94A3B8" },
];

const NEUTRAL_SHADES = [
    "#FFFFFF", "#F1F1F3", "#D9D9DE", "#B0B0B8", "#7C7C86", "#4A4A54", "#1F1F26", "#000000",
];

const FONT_OPTIONS = ["Inter", "Poppins", "Roboto", "Source Serif 4", "Space Grotesk"];

const getFontCss = (fontName: string) => {
    if (fontName === "Source Serif 4") return "'Source Serif 4', Georgia, serif";
    return `'${fontName}', -apple-system, BlinkMacSystemFont, sans-serif`;
};

const LAYOUT_MODES: Array<{ value: DesignTokens["layoutMode"]; label: string }> = [
    { value: "top-nav", label: "Top Nav" },
    { value: "side-nav", label: "Side Nav" },
    { value: "drawer", label: "Drawer" },
];

export default function DesignSection({ srs, onApprove }: DesignSectionProps) {
    const [colorMode, setColorMode] = useState<"preset" | "custom">("preset");
    const [showColorModal, setShowColorModal] = useState(true);
    const [selectedPreset, setSelectedPreset] = useState(0);
    const [customColors, setCustomColors] = useState({
        primary: "#FF6B6B",
        secondary: "#39605D",
        accent: "#FFE66D",
    });
    const [headingFont, setHeadingFont] = useState(FONT_OPTIONS[0]);
    const [bodyFont, setBodyFont] = useState(FONT_OPTIONS[1]);
    const [layoutMode, setLayoutMode] = useState<DesignTokens["layoutMode"]>("top-nav");
    const [theme, setTheme] = useState<DesignTokens["theme"]>("light");

    const activePreset = COLOR_PRESETS[selectedPreset];
    const activeColors = colorMode === "custom" ? customColors : activePreset;
    const screenCount = srs?.sitemap?.nodes?.length ?? 8;

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

            <div className="design-panel__body">
                <div className="design-panel__main">
                    <div className="palette-section">
                        <div className="palette-section__header">
                            <h2>Colors</h2>
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
                        </div>

                        <div className="palette-grid-wide">
                            <div className="palette-neutrals-card">
                                <span className="palette-card__name palette-card__name--dark">Neutrals</span>
                                <div className="palette-neutrals-strip">
                                    {NEUTRAL_SHADES.map((shade) => (
                                        <span key={shade} style={{ backgroundColor: shade }} />
                                    ))}
                                </div>
                            </div>

                            {colorMode === "preset" ? (
                                <>
                                    <button
                                        type="button"
                                        aria-pressed
                                        onClick={() => {}}
                                        className="palette-card palette-card--main"
                                        style={{ backgroundColor: activePreset.primary }}
                                    >
                                        <span className="palette-card__name">{activePreset.name}</span>
                                        <div>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex">
                                                    {activePreset.primary.toUpperCase()}
                                                </span>
                                                <span className="palette-card__badge">Main</span>
                                            </div>
                                            <div className="palette-card__shades">
                                                <span style={{ background: "rgba(255,255,255,0.7)" }} />
                                                <span style={{ background: "rgba(255,255,255,0.5)" }} />
                                                <span style={{ background: "rgba(0,0,0,0.15)" }} />
                                                <span style={{ background: "rgba(0,0,0,0.3)" }} />
                                            </div>
                                        </div>
                                    </button>

                                    <div className="palette-card-pair">
                                        <button
                                            type="button"
                                            className="palette-card"
                                            style={{ backgroundColor: activePreset.secondary }}
                                            onClick={() => {}}
                                        >
                                            <span className="palette-card__name">{activePreset.name.slice(0, 5)}...</span>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex">
                                                    {activePreset.secondary.toUpperCase()}
                                                </span>
                                            </div>
                                        </button>
                                        <button
                                            type="button"
                                            className="palette-card"
                                            style={{ backgroundColor: activePreset.accent }}
                                            onClick={() => {}}
                                        >
                                            <span className="palette-card__name" style={{ color: "#3c2854" }}>Accent</span>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex" style={{ color: "#3c2854" }}>
                                                    {activePreset.accent.toUpperCase()}
                                                </span>
                                            </div>
                                        </button>
                                    </div>

                                    <div className="palette-add-card">
                                        <span className="palette-add-card__plus">+</span>
                                        <div className="palette-swap-card__row">
                                            {COLOR_PRESETS.map((preset, index) => (
                                                <button
                                                    key={preset.name}
                                                    type="button"
                                                    title={preset.name}
                                                    aria-pressed={selectedPreset === index}
                                                    onClick={() => setSelectedPreset(index)}
                                                    className={
                                                        "palette-swap-dot" +
                                                        (selectedPreset === index ? " palette-swap-dot--selected" : "")
                                                    }
                                                    style={{ backgroundColor: preset.primary }}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <label
                                        className="palette-card palette-card--main palette-card--custom"
                                        style={{ backgroundColor: customColors.primary }}
                                    >
                                        <input
                                            type="color"
                                            className="palette-card__input"
                                            value={customColors.primary}
                                            onChange={(e) =>
                                                setCustomColors((prev) => ({ ...prev, primary: e.target.value }))
                                            }
                                        />
                                        <span className="palette-card__name">Primary</span>
                                        <div>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex">
                                                    {customColors.primary.toUpperCase()}
                                                </span>
                                                <span className="palette-card__badge">Main</span>
                                            </div>
                                            <div className="palette-card__shades">
                                                <span style={{ background: "rgba(255,255,255,0.7)" }} />
                                                <span style={{ background: "rgba(255,255,255,0.5)" }} />
                                                <span style={{ background: "rgba(0,0,0,0.15)" }} />
                                                <span style={{ background: "rgba(0,0,0,0.3)" }} />
                                            </div>
                                        </div>
                                    </label>

                                    <div className="palette-card-pair">
                                        <label
                                            className="palette-card palette-card--custom"
                                            style={{ backgroundColor: customColors.secondary }}
                                        >
                                            <input
                                                type="color"
                                                className="palette-card__input"
                                                value={customColors.secondary}
                                                onChange={(e) =>
                                                    setCustomColors((prev) => ({ ...prev, secondary: e.target.value }))
                                                }
                                            />
                                            <span className="palette-card__name">Secondary</span>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex">
                                                    {customColors.secondary.toUpperCase()}
                                                </span>
                                            </div>
                                        </label>
                                        <label
                                            className="palette-card palette-card--custom"
                                            style={{ backgroundColor: customColors.accent }}
                                        >
                                            <input
                                                type="color"
                                                className="palette-card__input"
                                                value={customColors.accent}
                                                onChange={(e) =>
                                                    setCustomColors((prev) => ({ ...prev, accent: e.target.value }))
                                                }
                                            />
                                            <span className="palette-card__name" style={{ color: "#3c2854" }}>Accent</span>
                                            <div className="palette-card__bottom">
                                                <span className="palette-card__hex" style={{ color: "#3c2854" }}>
                                                    {customColors.accent.toUpperCase()}
                                                </span>
                                            </div>
                                        </label>
                                    </div>

                                    <div className="palette-add-card">
                                        <span className="palette-add-card__plus">+</span>
                                        <span>Click color card to customize</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="typography-section">
                        <h2>Typography</h2>
                        <div className="typography-grid-wide">
                            <div className="typography-card">
                                <span className="typography-card__label">Heading</span>
                                <div
                                    className="typography-card__sample"
                                    style={{ fontFamily: headingFont }}
                                >
                                    {headingFont}
                                </div>
                                <div className="typography-card__meta">
                                    <span className="typography-card__google">G Google</span>
                                    <span>Free</span>
                                </div>
                                <select
                                    value={headingFont}
                                    onChange={(e) => setHeadingFont(e.target.value)}
                                >
                                    {FONT_OPTIONS.map((font) => (
                                        <option key={font} value={font} style={{ fontFamily: font }}>
                                            {font}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="typography-card">
                                <span className="typography-card__label">Body</span>
                                <div
                                    className="typography-card__sample"
                                    style={{ fontFamily: bodyFont }}
                                >
                                    {bodyFont}
                                </div>
                                <div className="typography-card__meta">
                                    <span className="typography-card__google">G Google</span>
                                    <span>Free</span>
                                </div>
                                <select
                                    value={bodyFont}
                                    onChange={(e) => setBodyFont(e.target.value)}
                                >
                                    {FONT_OPTIONS.map((font) => (
                                        <option key={font} value={font} style={{ fontFamily: font }}>
                                            {font}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="layout-theme-section">
                        <h2>Layout &amp; Theme</h2>
                        <div className="layout-theme-grid">
                            <div>
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
                            </div>

                            <div>
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
                        </div>
                    </div>
                </div>

                <div className="design-panel__preview-col">
                    <div className="design-preview-sticky">
                        <div className="design-preview-header">
                            <span className="design-preview-sticky__label">Mobile Screen Preview</span>
                            <span className="design-preview-sublabel">Live preview adapts to your palette &amp; typography</span>
                        </div>
                        
                        <div className="design-preview">
                            <div
                                className="mobile-phone-frame"
                                style={{
                                    backgroundColor: theme === "dark" ? "#0F172A" : "#F8FAFC",
                                    color: theme === "dark" ? "#F8FAFC" : "#0F172A",
                                    fontFamily: getFontCss(bodyFont),
                                }}
                            >
                                {/* Phone Notch / Dynamic Island */}
                                <div className="mobile-dynamic-island">
                                    <span className="camera-lens" />
                                </div>

                                {/* Phone Status Bar */}
                                <div
                                    className="mobile-status-bar"
                                    style={{
                                        backgroundColor: activeColors.primary,
                                        color: "#FFFFFF",
                                    }}
                                >
                                    <span className="status-time">9:41</span>
                                    <div className="status-icons">
                                        <svg width="12" height="9" viewBox="0 0 14 10" fill="currentColor">
                                            <rect x="0" y="7" width="2" height="3" rx="0.5" />
                                            <rect x="4" y="5" width="2" height="5" rx="0.5" />
                                            <rect x="8" y="2" width="2" height="8" rx="0.5" />
                                            <rect x="12" y="0" width="2" height="10" rx="0.5" />
                                        </svg>
                                        <span style={{ fontSize: "9px" }}>5G</span>
                                        <svg width="16" height="8" viewBox="0 0 18 9" fill="currentColor">
                                            <rect x="0.5" y="0.5" width="14" height="8" rx="2" stroke="currentColor" fill="none" />
                                            <rect x="2" y="2" width="9" height="5" rx="1" />
                                            <path d="M16 3.5V5.5" stroke="currentColor" strokeLinecap="round" />
                                        </svg>
                                    </div>
                                </div>

                                {/* Mobile App Main Scroll Area */}
                                <div className="mobile-phone-content">
                                    {/* Minimal App Header */}
                                    <div
                                        className="mobile-app-header-minimal"
                                        style={{
                                            backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                            borderBottom: `1px solid ${theme === "dark" ? "#334155" : "#E2E8F0"}`,
                                        }}
                                    >
                                        <div className="mobile-search-pill" style={{ backgroundColor: theme === "dark" ? "#334155" : "#F1F5F9" }}>
                                            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                                                <circle cx="7" cy="7" r="5" />
                                                <path d="M11 11L15 15" />
                                            </svg>
                                            <span style={{ fontFamily: getFontCss(bodyFont) }}>Search</span>
                                        </div>
                                        <div
                                            className="mobile-header-avatar-circle"
                                            style={{ backgroundColor: activeColors.primary, color: "#FFFFFF" }}
                                        >
                                            <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                                                <path d="M8 0L10.2 5.8L16 8L10.2 10.2L8 16L5.8 10.2L0 8L5.8 5.8L8 0Z" />
                                            </svg>
                                        </div>
                                    </div>

                                    {/* Minimal Story Circles (Primary Outline Only) */}
                                    <div className="mobile-stories-minimal">
                                        <div className="mobile-story-circle" style={{ borderColor: activeColors.primary, backgroundColor: "transparent" }}>
                                            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" style={{ color: activeColors.primary }}>
                                                <path d="M8 0L10.2 5.8L16 8L10.2 10.2L8 16L5.8 10.2L0 8L5.8 5.8L8 0Z" />
                                            </svg>
                                        </div>
                                        <div className="mobile-story-circle" style={{ borderColor: activeColors.primary, backgroundColor: "transparent" }}>
                                            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" style={{ color: activeColors.primary }}>
                                                <rect x="3" y="3" width="10" height="10" rx="2" />
                                            </svg>
                                        </div>
                                        <div className="mobile-story-circle" style={{ borderColor: activeColors.primary, backgroundColor: "transparent" }}>
                                            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" style={{ color: activeColors.primary }}>
                                                <polygon points="8,2 15,14 1,14" />
                                            </svg>
                                        </div>
                                        <div className="mobile-story-circle" style={{ borderColor: activeColors.primary, backgroundColor: "transparent" }}>
                                            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" style={{ color: activeColors.primary }}>
                                                <path d="M8 1L14 4.5V11.5L8 15L2 11.5V4.5L8 1Z" />
                                            </svg>
                                        </div>
                                    </div>

                                    {/* Minimal Hero Visual Banner (Solid Major Primary Color - NO Gradient) */}
                                    <div
                                        className="mobile-hero-minimal"
                                        style={{
                                            backgroundColor: activeColors.primary,
                                            color: "#FFFFFF",
                                        }}
                                    >
                                        <div className="mobile-hero-icon-box" style={{ backgroundColor: "rgba(255,255,255,0.2)" }}>
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <rect x="3" y="3" width="18" height="18" rx="4" />
                                                <path d="M3 9H21" />
                                                <path d="M9 21V9" />
                                            </svg>
                                        </div>
                                        <div className="mobile-hero-info">
                                            <h4 style={{ fontFamily: getFontCss(headingFont) }}>App Prototype</h4>
                                            <span style={{ fontFamily: getFontCss(bodyFont) }}>{screenCount} Generated Screens</span>
                                        </div>
                                        <button
                                            type="button"
                                            className="mobile-hero-pill-btn"
                                            style={{
                                                backgroundColor: "rgba(255,255,255,0.25)",
                                                color: "#FFFFFF",
                                                fontFamily: getFontCss(headingFont),
                                            }}
                                        >
                                            View
                                        </button>
                                    </div>

                                    {/* Minimal Cards Grid (4 Cards Total - Secondary Color Icons & Badges) */}
                                    <div className="mobile-cards-grid-minimal">
                                        <div
                                            className="mobile-grid-card-minimal"
                                            style={{
                                                backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                                borderColor: `${activeColors.secondary}44`,
                                            }}
                                        >
                                            <div
                                                className="mobile-card-preview-block"
                                                style={{
                                                    backgroundColor: theme === "dark" ? "rgba(255,255,255,0.06)" : "#F1F5F9",
                                                    color: activeColors.secondary,
                                                }}
                                            >
                                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M18 20V10" />
                                                    <path d="M12 20V4" />
                                                    <path d="M6 20V14" />
                                                </svg>
                                            </div>
                                            <div className="mobile-card-meta">
                                                <strong style={{ fontFamily: getFontCss(headingFont) }}>Dashboard</strong>
                                                <span className="mobile-badge-pill" style={{ backgroundColor: activeColors.secondary, color: "#FFF" }}>
                                                    Main
                                                </span>
                                            </div>
                                        </div>

                                        <div
                                            className="mobile-grid-card-minimal"
                                            style={{
                                                backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                                borderColor: `${activeColors.secondary}44`,
                                            }}
                                        >
                                            <div
                                                className="mobile-card-preview-block"
                                                style={{
                                                    backgroundColor: theme === "dark" ? "rgba(255,255,255,0.06)" : "#F1F5F9",
                                                    color: activeColors.secondary,
                                                }}
                                            >
                                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <circle cx="12" cy="12" r="3" />
                                                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                                                </svg>
                                            </div>
                                            <div className="mobile-card-meta">
                                                <strong style={{ fontFamily: getFontCss(headingFont) }}>Settings</strong>
                                                <span className="mobile-badge-pill" style={{ backgroundColor: activeColors.secondary, color: "#FFF" }}>
                                                    Theme
                                                </span>
                                            </div>
                                        </div>

                                        <div
                                            className="mobile-grid-card-minimal"
                                            style={{
                                                backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                                borderColor: `${activeColors.secondary}44`,
                                            }}
                                        >
                                            <div
                                                className="mobile-card-preview-block"
                                                style={{
                                                    backgroundColor: theme === "dark" ? "rgba(255,255,255,0.06)" : "#F1F5F9",
                                                    color: activeColors.secondary,
                                                }}
                                            >
                                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                                                </svg>
                                            </div>
                                            <div className="mobile-card-meta">
                                                <strong style={{ fontFamily: getFontCss(headingFont) }}>Analytics</strong>
                                                <span className="mobile-badge-pill" style={{ backgroundColor: activeColors.secondary, color: "#FFF" }}>
                                                    Stats
                                                </span>
                                            </div>
                                        </div>

                                        <div
                                            className="mobile-grid-card-minimal"
                                            style={{
                                                backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                                borderColor: `${activeColors.secondary}44`,
                                            }}
                                        >
                                            <div
                                                className="mobile-card-preview-block"
                                                style={{
                                                    backgroundColor: theme === "dark" ? "rgba(255,255,255,0.06)" : "#F1F5F9",
                                                    color: activeColors.secondary,
                                                }}
                                            >
                                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <rect x="3" y="3" width="7" height="7" rx="1" />
                                                    <rect x="14" y="3" width="7" height="7" rx="1" />
                                                    <rect x="14" y="14" width="7" height="7" rx="1" />
                                                    <rect x="3" y="14" width="7" height="7" rx="1" />
                                                </svg>
                                            </div>
                                            <div className="mobile-card-meta">
                                                <strong style={{ fontFamily: getFontCss(headingFont) }}>Overview</strong>
                                                <span className="mobile-badge-pill" style={{ backgroundColor: activeColors.secondary, color: "#FFF" }}>
                                                    Live
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Minimal Color Bar Indicator */}
                                    <div
                                        className="mobile-color-strip-minimal"
                                        style={{
                                            backgroundColor: theme === "dark" ? "#1E293B" : "#FFFFFF",
                                            borderColor: `${activeColors.primary}22`,
                                        }}
                                    >
                                        <div className="mobile-color-dots">
                                            <span style={{ backgroundColor: activeColors.primary }} />
                                            <span style={{ backgroundColor: activeColors.secondary }} />
                                            <span style={{ backgroundColor: activeColors.accent }} />
                                        </div>
                                        <span className="mobile-color-label" style={{ fontFamily: getFontCss(bodyFont) }}>
                                            {activeColors.primary.toUpperCase()}
                                        </span>
                                    </div>

                                    {/* Dedicated Bottom Action Button in Tertiary Accent Color */}
                                    <div className="mobile-bottom-action-container">
                                        <button
                                            type="button"
                                            className="mobile-tertiary-action-btn"
                                            style={{
                                                backgroundColor: activeColors.accent,
                                                color: "#1E122A",
                                                fontFamily: getFontCss(headingFont),
                                            }}
                                        >
                                            Continue
                                        </button>
                                    </div>
                                </div>

                                {/* Mobile Bottom Navigation Bar */}
                                <div
                                    className="mobile-bottom-nav"
                                    style={{
                                        backgroundColor: theme === "dark" ? "#0F172A" : "#FFFFFF",
                                        borderTopColor: theme === "dark" ? "#334155" : "#E2E8F0",
                                    }}
                                >
                                    <button type="button" className="mobile-nav-tab active" style={{ color: activeColors.primary }}>
                                        <span className="nav-icon">
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                                                <polyline points="9 22 9 12 15 12 15 22" />
                                            </svg>
                                        </span>
                                        <span className="nav-text" style={{ fontFamily: getFontCss(bodyFont) }}>Home</span>
                                    </button>
                                    <button type="button" className="mobile-nav-tab">
                                        <span className="nav-icon">
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <circle cx="11" cy="11" r="8" />
                                                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                                            </svg>
                                        </span>
                                        <span className="nav-text" style={{ fontFamily: getFontCss(bodyFont) }}>Explore</span>
                                    </button>
                                    <button type="button" className="mobile-nav-tab">
                                        <span className="nav-icon">
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                                            </svg>
                                        </span>
                                        <span className="nav-text" style={{ fontFamily: getFontCss(bodyFont) }}>Activity</span>
                                    </button>
                                    <button type="button" className="mobile-nav-tab">
                                        <span className="nav-icon">
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                                <circle cx="12" cy="7" r="4" />
                                            </svg>
                                        </span>
                                        <span className="nav-text" style={{ fontFamily: getFontCss(bodyFont) }}>Profile</span>
                                    </button>
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