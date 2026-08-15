import type { DesignTokens } from "../design/DesignSection";

interface LayoutNode {
    component_type?: string;
    type?: string;
    props?: Record<string, any>;
    children?: LayoutNode[];
}

interface ScreenRendererProps {
    layout: LayoutNode;
    screenName: string;
    designTokens?: DesignTokens | null;
}

function buildColors(tokens?: DesignTokens | null) {
    const isDark = tokens?.theme === "dark";
    return {
        primary: tokens?.colors?.primary || "#2563EB",
        onPrimary: "#FFFFFF",
        background: isDark ? "#0F172A" : "#F8FAFC",
        surface: isDark ? "#1E293B" : "#FFFFFF",
        text: isDark ? "#F1F5F9" : "#1E293B",
        subtleText: isDark ? "#94A3B8" : "#64748B",
        border: isDark ? "#334155" : "#E2E8F0",
        placeholder: isDark ? "#334155" : "#E2E8F0",
    };
}

function getType(node: LayoutNode): string {
    return node.component_type || node.type || "View";
}

function getLabel(node: LayoutNode): string | undefined {
    const props = node.props || {};
    return props.label || props.title || props.text || props.placeholder;
}

function renderChildren(
    children: LayoutNode[] | undefined,
    keyPrefix: string,
    colors: ReturnType<typeof buildColors>,
    fontFamily: string
) {
    if (!children || children.length === 0) return null;
    return children.map((child, index) => (
        <RenderNode
            key={`${keyPrefix}-${index}`}
            node={child}
            keyPrefix={`${keyPrefix}-${index}`}
            colors={colors}
            fontFamily={fontFamily}
        />
    ));
}

function RenderNode({
    node,
    keyPrefix,
    colors,
    fontFamily,
}: {
    node: LayoutNode;
    keyPrefix: string;
    colors: ReturnType<typeof buildColors>;
    fontFamily: string;
}) {
    const type = getType(node);
    const label = getLabel(node);
    const children = node.children;

    switch (type) {
        case "Header":
            return (
                <div
                    style={{
                        padding: "14px 16px",
                        borderBottom: `1px solid ${colors.border}`,
                        fontWeight: 700,
                        fontSize: 16,
                        color: colors.text,
                        background: colors.surface,
                        fontFamily,
                    }}
                >
                    {label || "Header"}
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );

        case "Navbar":
        case "Footer":
            return (
                <div
                    style={{
                        display: "flex",
                        flexDirection: "row",
                        justifyContent: "space-around",
                        alignItems: "center",
                        padding: "10px 8px",
                        borderTop: `1px solid ${colors.border}`,
                        background: colors.surface,
                    }}
                >
                    {children && children.length > 0 ? (
                        renderChildren(children, keyPrefix, colors, fontFamily)
                    ) : (
                        <>
                            <span style={{ color: colors.primary, fontSize: 18 }}>●</span>
                            <span style={{ color: colors.subtleText, fontSize: 18 }}>●</span>
                            <span style={{ color: colors.subtleText, fontSize: 18 }}>●</span>
                        </>
                    )}
                </div>
            );

        case "Card":
            return (
                <div
                    style={{
                        background: colors.surface,
                        border: `1px solid ${colors.border}`,
                        borderRadius: 12,
                        padding: 12,
                        display: "flex",
                        flexDirection: "column",
                        gap: 8,
                        boxShadow: "0 1px 4px rgba(15, 23, 42, 0.06)",
                    }}
                >
                    {label && (
                        <span style={{ fontSize: 13, fontWeight: 600, color: colors.text, fontFamily }}>
                            {label}
                        </span>
                    )}
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );

        case "Row":
            return (
                <div style={{ display: "flex", flexDirection: "row", gap: 8, alignItems: "center" }}>
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );

        case "Column":
            return (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );

        case "SafeAreaView":
        case "Screen":
        case "Container":
        case "ScrollView":
            return (
                <div
                    style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 10,
                        flex: 1,
                        padding: type === "ScrollView" ? 0 : 12,
                        background: colors.background,
                    }}
                >
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );

        case "SearchBar":
            return (
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        border: `1px solid ${colors.border}`,
                        borderRadius: 10,
                        padding: "8px 12px",
                        background: colors.surface,
                        fontSize: 13,
                        color: colors.subtleText,
                        fontFamily,
                    }}
                >
                    <span>🔍</span>
                    <span>{label || "Search"}</span>
                </div>
            );

        case "TextInput":
        case "FormField":
            return (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {label && (
                        <span style={{ fontSize: 12, color: colors.subtleText, fontFamily }}>{label}</span>
                    )}
                    <div
                        style={{
                            border: `1px solid ${colors.border}`,
                            borderRadius: 8,
                            padding: "9px 10px",
                            background: colors.surface,
                            fontSize: 13,
                            color: colors.subtleText,
                            fontFamily,
                        }}
                    >
                        {type === "FormField" ? "" : label || "Enter text..."}
                    </div>
                </div>
            );

        case "Button":
            return (
                <div
                    style={{
                        background: colors.primary,
                        color: colors.onPrimary,
                        borderRadius: 10,
                        padding: "10px 14px",
                        textAlign: "center",
                        fontSize: 13,
                        fontWeight: 600,
                        fontFamily,
                    }}
                >
                    {label || "Button"}
                </div>
            );

        case "Avatar":
            return (
                <div
                    style={{
                        width: 36,
                        height: 36,
                        borderRadius: "50%",
                        background: colors.placeholder,
                        flexShrink: 0,
                    }}
                />
            );

        case "Image":
            return (
                <div
                    style={{
                        width: "100%",
                        height: 90,
                        borderRadius: 8,
                        background: colors.placeholder,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 18,
                        color: colors.subtleText,
                    }}
                >
                    🖼️
                </div>
            );

        case "ItemCard":
            return (
                <div
                    style={{
                        border: `1px solid ${colors.border}`,
                        borderRadius: 10,
                        padding: 8,
                        display: "flex",
                        flexDirection: "column",
                        gap: 6,
                        background: colors.surface,
                    }}
                >
                    <div style={{ width: "100%", height: 60, borderRadius: 6, background: colors.placeholder }} />
                    <div style={{ width: "70%", height: 8, borderRadius: 4, background: colors.border }} />
                    <div style={{ width: "40%", height: 8, borderRadius: 4, background: colors.border }} />
                </div>
            );

        case "FlatList": {
            const numColumns = Number(node.props?.numColumns) || 1;
            const template = children && children.length > 0 ? children[0] : null;
            const items = template ? [template, template] : [];

            return (
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: `repeat(${numColumns}, 1fr)`,
                        gap: 8,
                    }}
                >
                    {items.length > 0 ? (
                        items.map((item, index) => (
                            <RenderNode
                                key={`${keyPrefix}-fl-${index}`}
                                node={item}
                                keyPrefix={`${keyPrefix}-fl-${index}`}
                                colors={colors}
                                fontFamily={fontFamily}
                            />
                        ))
                    ) : (
                        <span style={{ fontSize: 12, color: colors.subtleText }}>(empty list)</span>
                    )}
                </div>
            );
        }

        default:
            // Unknown component_type — still render it (mirrors the
            // backend fallback renderer treating unknown types as a
            // generic container) instead of silently dropping the node.
            return (
                <div
                    style={{
                        border: `1px dashed ${colors.border}`,
                        borderRadius: 8,
                        padding: 8,
                        display: "flex",
                        flexDirection: "column",
                        gap: 6,
                    }}
                >
                    <span style={{ fontSize: 10, color: colors.subtleText, textTransform: "uppercase" }}>
                        {type}
                    </span>
                    {label && <span style={{ fontSize: 13, color: colors.text, fontFamily }}>{label}</span>}
                    {renderChildren(children, keyPrefix, colors, fontFamily)}
                </div>
            );
    }
}

export default function ScreenRenderer({ layout, screenName, designTokens }: ScreenRendererProps) {
    const colors = buildColors(designTokens);
    const fontFamily = designTokens?.typography?.bodyFont
        ? `"${designTokens.typography.bodyFont}", sans-serif`
        : undefined;

    if (!layout || Object.keys(layout).length === 0) {
        return (
            <div
                style={{
                    padding: 24,
                    textAlign: "center",
                    color: colors.subtleText,
                    fontSize: 13,
                }}
            >
                No layout available for this screen.
            </div>
        );
    }

    return (
        <div
            style={{
                width: 300,
                margin: "0 auto",
                borderRadius: 32,
                border: "10px solid #1f1830",
                background: "#1f1830",
                boxShadow: "0 12px 30px rgba(15, 23, 42, 0.25)",
                overflow: "hidden",
            }}
        >
            <div
                style={{
                    background: colors.background,
                    minHeight: 560,
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        padding: "8px 16px 0",
                        fontSize: 11,
                        color: colors.subtleText,
                        fontFamily,
                    }}
                >
                    <span>9:41</span>
                    <span>{screenName}</span>
                </div>

                <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                    <RenderNode node={layout} keyPrefix="root" colors={colors} fontFamily={fontFamily || "inherit"} />
                </div>
            </div>
        </div>
    );
}
