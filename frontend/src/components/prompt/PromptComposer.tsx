import { useEffect, useState } from "react";
import { generateSRS } from "../../services/JinieService";

interface PromptComposerProps {
    initialPrompt?: string;
    onSubmit: (prompt: string, srs: any) => void;
}

export default function PromptComposer({
    initialPrompt = "",
    onSubmit,
}: PromptComposerProps) {
    const [prompt, setPrompt] = useState(initialPrompt);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        setPrompt(initialPrompt);
    }, [initialPrompt]);

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            setError("Please enter a project description.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const result = await generateSRS(prompt);

            console.log("Generated SRS:", result);

            // Send both prompt and generated SRS to WorkspacePage
            onSubmit(prompt, result);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to generate SRS."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the application you want to build..."
            />

            <button onClick={handleGenerate} disabled={loading}>
                {loading ? "Generating SRS..." : "Generate SRS"}
            </button>

            {error && <p>{error}</p>}
        </div>
    );
}