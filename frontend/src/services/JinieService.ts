const API_BASE_URL = "http://127.0.0.1:8000";

export interface SRSProgress {
    type: "progress" | "complete" | "error";
    progress?: number;
    stage?: string;
    message?: string;
    result?: any;
}

export async function generateSRS(prompt: string) {
    const response = await fetch(
        `${API_BASE_URL}/api/srs/generate`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                prompt,
            }),
        }
    );

    if (!response.ok) {
        const text = await response.text();

        throw new Error(
            `SRS generation failed: ${response.status} ${text}`
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
    const trees = Array.isArray(componentTrees)
        ? componentTrees
        : componentTrees?.trees ?? [];

    const response = await fetch(
        `${API_BASE_URL}/api/components/generate`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                trace_id:
                    traceId ??
                    (Array.isArray(componentTrees)
                        ? undefined
                        : componentTrees?.trace_id),
                component_trees: trees,
                design_tokens: designTokens,
                tech_stack: techStack,
            }),
        }
    );

    if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
            `Component generation failed: ${response.status} ${errorText}`
        );
    }

    return await response.json();
}

export async function generateSRSWithProgress(
    prompt: string,
    onProgress: (update: SRSProgress) => void
) {
    const response = await fetch(
        `${API_BASE_URL}/api/srs/generate-stream`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                prompt,
            }),
        }
    );

    if (!response.ok) {
        const text = await response.text();

        throw new Error(
            `SRS generation failed: ${response.status} ${text}`
        );
    }

    if (!response.body) {
        throw new Error("Browser does not support streaming.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const event of events) {
            const line = event
                .split("\n")
                .find((line) => line.startsWith("data:"));

            if (!line) {
                continue;
            }

            const jsonString = line
                .replace(/^data:\s*/, "")
                .trim();

            if (!jsonString) {
                continue;
            }

            try {
                const data: SRSProgress = JSON.parse(jsonString);

                console.log("SRS EVENT:", data);

                onProgress(data);

                if (data.type === "error") {
                    throw new Error(
                        data.message || "SRS generation failed."
                    );
                }

                if (data.type === "complete") {
                    return data.result;
                }
            } catch (error) {
                console.error(
                    "SRS event parsing error:",
                    error
                );

                throw error;
            }
        }
    }

    throw new Error(
        "SRS stream ended without completing."
    );
}