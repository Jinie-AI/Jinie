const API_BASE_URL = "http://127.0.0.1:8000";


export async function generateSRS(prompt: string) {
    const response = await fetch(`${API_BASE_URL}/api/srs/generate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prompt: prompt,
        }),
    });

    if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
            `SRS generation failed: ${response.status} ${errorText}`
        );
    }

    return await response.json();
}


export async function generateComponents(
    componentTrees: { trace_id?: string; trees: any[] } | any[],
    designTokens: Record<string, unknown>,
    techStack?: Record<string, unknown>,
    traceId?: string
) {
    // Accept either the raw ComponentTreeSet shape ({trace_id, trees})
    // that the SRS pipeline returns, or an already-unwrapped trees array.
    const trees = Array.isArray(componentTrees)
        ? componentTrees
        : componentTrees?.trees ?? [];

    const response = await fetch(`${API_BASE_URL}/api/components/generate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            trace_id: traceId ?? (Array.isArray(componentTrees) ? undefined : componentTrees?.trace_id),
            component_trees: trees,
            design_tokens: designTokens,
            tech_stack: techStack,
        }),
    });

    if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
            `Component generation failed: ${response.status} ${errorText}`
        );
    }

    return await response.json();
}