import { useState } from "react";
import { useNavigate } from "react-router-dom";
import jinieLogo from "../assets/logo_jinie.png";
import { generateSRS } from "../services/JinieService";

export default function HomePage() {
    const [prompt, setPrompt] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    const handleGenerate = async () => {
        if (!prompt.trim() || isGenerating) return;

        setIsGenerating(true);
        setErrorMessage("");

        try {
            const srs = await generateSRS(prompt);

            localStorage.setItem("jinie_prompt", prompt);
            localStorage.setItem("jinie_srs", JSON.stringify(srs));
            // A fresh prompt means a fresh run — clear anything left over
            // from a previous session so the workspace doesn't reopen on
            // stale design tokens or an old stage.
            localStorage.removeItem("jinie_design_tokens");
            localStorage.removeItem("jinie_stage");

            navigate("/workspace");
        } catch (error) {
            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "SRS generation failed. Please try again."
            );
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="home-page">
            <header className="home-header">
                <div className="logo">
                    <img src={jinieLogo} alt="Jinie" className="logo-image" />
                    <span>Jinie</span>
                </div>

                <div className="header-actions">
                    <button className="secondary-button">Documentation</button>
                    <button className="secondary-button">GitHub</button>
                </div>
            </header>

            <main className="home-content">
                <h1>
                    Turn your idea into an
                    <span> application.</span>
                </h1>

                <p className="hero-description">
                    Describe what you want to build and Jinie will transform
                    your idea into a complete software plan.
                </p>

                <div className="prompt-card">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the application you want to build..."
                        rows={6}
                        disabled={isGenerating}
                    />

                    <div className="prompt-footer">
                        <span className="prompt-hint">
                            {errorMessage && <span className="home-error">{errorMessage}</span>}
                        </span>

                        <button
                            className="primary-button"
                            onClick={handleGenerate}
                            disabled={!prompt.trim() || isGenerating}
                        >
                            {isGenerating ? "Generating…" : "Generate"}
                            <span>→</span>
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}